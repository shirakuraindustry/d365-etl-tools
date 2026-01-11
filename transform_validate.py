
# --- 追加 import ---
import unicodedata, re
from datetime import datetime
import pandas as pd
import sys
import logging

def _nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s)

def _trim_space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def normalize_text(s):
    if not isinstance(s, str):
        return s
    # Unicode正規化＋トリム＋連続空白・改行の正規化
    s = _nfkc(s)
    s = s.strip()
    s = re.sub(r'[\s\u3000]+', ' ', s)  # 全角スペースも
    s = re.sub(r'\n+', ' ', s)
    s = re.sub(r' +', ' ', s)
    return s

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def normalize_email(s):
    if not isinstance(s, str) or s == "":
        return s, False
    n = normalize_text(s).lower()
    ok = bool(_EMAIL_RE.match(n))
    return n, (not ok)

def normalize_phone_jp(s):
    if not isinstance(s, str) or not s.strip():
        return s, False
    digits = re.sub(r"\D", "", s)
    # 国番号81の処理：+81(0を除く) → 0始まりに戻す
    if digits.startswith("81") and len(digits) >= 10:
        if digits[2] != "0":
            digits = "0" + digits[2:]
        else:
            digits = digits[1:]  # 念のため
    # 090/080/070/050/固定電話対応
    if len(digits) == 10:
        fmt = f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
        return fmt, False
    if len(digits) == 11:
        fmt = f"{digits[0:3]}-{digits[3:7]}-{digits[7:11]}"
        return fmt, False
    return s, True  # 不正

def normalize_postal_jp(s):
    if not isinstance(s, str) or not s.strip():
        return s, False
    digits = re.sub(r"\D", "", s)
    if len(digits) == 7:
        return f"{digits[0:3]}-{digits[3:7]}", False
    return s, True

def normalize_date(s):
    if not isinstance(s, str) or not s.strip():
        return pd.NaT
    c = normalize_text(s)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return pd.to_datetime(datetime.strptime(c, fmt).date())
        except Exception:
            pass
    try:
        return pd.to_datetime(c, errors="coerce").date()
    except Exception:
        return pd.NaT

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.applymap(lambda v: normalize_text(v) if isinstance(v, str) else v)

    # email
    if "internalemailaddress" in df.columns:
        out, invalid = [], []
        for v in df["internalemailaddress"].tolist():
            n, bad = normalize_email(v)
            out.append(n)
            invalid.append(bad)
        df["internalemailaddress"] = out
        df["email_invalid"] = invalid

    # phone
    for col in ["mobilephone", "address1_telephone1"]:
        if col in df.columns:
            out, invalid = [], []
            for v in df[col].tolist():
                n, bad = normalize_phone_jp(v)
                out.append(n)
                invalid.append(bad)
            df[col] = out
            df[f"{col}_invalid"] = invalid

    # postal
    if "address1_postalcode" in df.columns:
        out, invalid = [], []
        for v in df["address1_postalcode"].tolist():
            n, bad = normalize_postal_jp(v)
            out.append(n)
            invalid.append(bad)
        df["address1_postalcode"] = out
        df["postal_invalid"] = invalid

    # dates
    for col in ["birthdate", "modifiedon"]:
        if col in df.columns:
            df[col] = df[col].apply(normalize_date)

    return df

def quality_report(df: pd.DataFrame, dupcol: str):
    logger = logging.getLogger("etl_quality")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    total = len(df) if len(df) > 0 else 1
    null_rates = df.isna().sum().div(total)

    dup_rate = (df.duplicated(subset=[dupcol]).sum() / total) if dupcol in df.columns else 0.0
    email_invalid_rate = df["email_invalid"].mean() if "email_invalid" in df.columns else 0.0

    inv_cols = [c for c in df.columns if c.endswith("_invalid")]
    invalid_rates = {c: float(df[c].mean()) for c in inv_cols}

    logger.info("=== Data Quality ===")
    logger.info(f"Rows: {len(df)}")
    logger.info(f"Max NULL rate: {null_rates.max():.2%}")
    logger.info(f"Duplicate rate ({dupcol}): {dup_rate:.2%}")
    logger.info(f"Email invalid rate: {email_invalid_rate:.2%}")
    for k, v in invalid_rates.items():
        logger.info(f"{k} rate: {v:.2%}")

    threshold_null = 0.02
    threshold_dup = 0.005
    threshold_invalid = 0.01
    if (null_rates.max() > threshold_null) or (dup_rate > threshold_dup) or \
       (email_invalid_rate > threshold_invalid) or \
       any(v > threshold_invalid for v in invalid_rates.values()):
        logger.error("Quality thresholds exceeded.")
        sys.exit(2)
