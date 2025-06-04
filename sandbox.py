import pandas as pd
import csv

file_path = "202401_PAX15min-ABC.csv"

try:
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', quoting=csv.QUOTE_NONE)

except FileNotFoundError:
    print(f"Error: El archivo {file_path} no se encontró.")
    df = pd.DataFrame()

print(df.columns.size)