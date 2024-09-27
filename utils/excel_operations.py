import pandas as pd
from openpyxl import load_workbook

def read_excel_file(file_name, sheet_name):
    return pd.read_excel(file_name, sheet_name=sheet_name)

def write_to_excel(df, file_name, sheet_name):
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

def generate_and_add_hashes(df, columns_to_hash, hashed_column_name, generate_hashes):
    if all(col in df.columns for col in columns_to_hash):
        df[hashed_column_name] = generate_hashes(df, columns_to_hash)
        print("DataFrame with hashes:\n", df)
    else:
        print("One or more specified columns are missing in the DataFrame.")
    return df

def update_column(df, column_name, data):
    if column_name not in df.columns:
        df[column_name] = None
    df[column_name] = data
    return df