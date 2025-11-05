
# d365-etl-tools

白倉工業 D365移行プロジェクトにおける ETL（抽出・変換・ロード）処理の技術リポジトリです。

## 📦 構成概要
├── schemas/         # スキーマ定義（JSON/YAML）
├── transform/       # Python変換コード
├── notebooks/       # Jupyterノートブック
├── config/          # ETL設定ファイル（Dataflow等）
├── tests/           # 単体テストコード
├── docs/            # 説明書・手順書

## 🧩 使用技術

- Python 3.10+
- Pandas / PyYAML / jsonschema
- Jupyter Notebook
- Azure Data Factory / Power Platform
- Git / Azure DevOps Repos

## 🚀 運用ルール

- ブランチ戦略：
  - `main`：承認済み成果物
  - `dev`：開発中統合
  - `feature/<業務名>-<処理名>`：個別作業
- Pull Request：
  - 技術レビュー：細内 雄太
  - 業務レビュー：大江 知広
- 命名規則・タグ設計は `/docs/schema_guidelines.md` を参照

## 📄 ライセンス

社内利用限定。外部公開・再配布は禁止。