import hashlib
import pandas as pd

def generate_hashes(df: pd.DataFrame, columns_to_hash: list) -> pd.Series:
    return df[columns_to_hash].astype(str).apply(lambda row: hashlib.sha256(''.join(row).encode()).hexdigest(), axis=1)