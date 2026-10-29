
import pandas as pd
import mysql.connector
from getpass import getpass

# CSV file path
csv_path = r"C:\Users\PRADIP\OneDrive\Desktop\Cash_Flow_Forecasting_and_Financial_Planning\data\cash_flow.csv"

# Read CSV
df = pd.read_csv(csv_path)

# Keep only the required columns
df = df[
    [
        "date",
        "netIncome",
        "operatingCashFlow",
        "capitalExpenditure",
        "freeCashFlow"
    ]
].copy()

# Extract year from date
df["year"] = pd.to_datetime(df["date"]).dt.year

# Rename columns to match MySQL table
df = df[
    [
        "year",
        "netIncome",
        "operatingCashFlow",
        "capitalExpenditure",
        "freeCashFlow"
    ]
]
df.columns = [
    "year",
    "net_income",
    "operating_cash_flow",
    "capital_expenditure",
    "free_cash_flow"
]

# Connect to MySQL
password = getpass("Enter your MySQL root password: ")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="cash_flow_db"
)

cursor = connection.cursor()

# Insert data into table
query = """
INSERT INTO cash_flow
(year, net_income, operating_cash_flow,
 capital_expenditure, free_cash_flow)
VALUES (%s, %s, %s, %s, %s)
"""

rows = [
    tuple(None if pd.isna(value) else value for value in row)
    for row in df.itertuples(index=False, name=None)
]

cursor.executemany(query, rows)
connection.commit()

print("Rows inserted:", cursor.rowcount)

cursor.close()
connection.close()

print("Data imported successfully!")
