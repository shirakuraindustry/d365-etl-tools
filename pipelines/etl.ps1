
function Invoke-WithRetry {
  param([ScriptBlock]$Script, [int]$Max=3)
  $delay = 5
  for ($i=1; $i -le $Max; $i++) {
    try { & $Script; return }
    catch {
      $jitter = Get-Random -Minimum 0 -Maximum 3
      $backoff = [math]::Pow($delay, $i) + $jitter
      Write-Warning "Attempt $i failed: $($_.Exception.Message)"
      if ($i -eq $Max) { throw }
      Start-Sleep -Seconds $backoff
    }
  }
}

function Main {
  $export = "$env:BUILD_ARTIFACTSTAGINGDIRECTORY/export.csv"
  $output = "$env:BUILD_ARTIFACTSTAGINGDIRECTORY/output.csv"

  Export-Entity

  Write-Host "== Transform & Validate =="
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $logTmp = [System.IO.Path]::Combine($env:TEMP, "etl_transform.log")
  python "$(Split-Path $PSCommandPath)/transform_validate.py" --input "$export" --output "$output" --dupcol "$DupColumn" *>&1 | Tee-Object -FilePath $logTmp
  $exit = $LASTEXITCODE
  $sw.Stop()
  if (Test-Path $output) {
    $fi = Get-Item $output
    Write-Host ("Transform elapsed: {0}s" -f [int]$sw.Elapsed.TotalSeconds)
    Write-Host ("Output size: {0} KB" -f [math]::Round($fi.Length/1KB,2))
    $header = (Get-Content $output -First 1)
    $colCount = ($header -split ",").Count
    $rowCount = (Get-Content $output | Measure-Object -Line).Lines - 1
    Write-Host "Output rows: $rowCount, columns: $colCount"
  }
  else {
    Write-Host ("Transform elapsed: {0}s" -f [int]$sw.Elapsed.TotalSeconds)
  }

  if ($exit -ne 0) {
    Write-Error "Transform/Validate failed with code $exit"
    if (Test-Path $logTmp) {
      Get-Content $logTmp -Tail 100 | %{ Write-Error $_ }
    }
    throw
  }

  Import-Entity -InputPath $output
}
