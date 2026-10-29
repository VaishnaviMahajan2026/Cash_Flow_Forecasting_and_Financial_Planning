
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
# Load API key from .env file
load_dotenv()

API_KEY = os.getenv("FMP_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Check your .env file.")

# Company symbol
SYMBOL = "AAPL"

# Create data folder if it does not exist
os.makedirs("data", exist_ok=True)

# FMP API endpoint
BASE_URL = "https://financialmodelingprep.com/stable"

# Financial statements to download
endpoints = {
    "cash_flow": "cash-flow-statement",
    "income_statement": "income-statement",
    "balance_sheet": "balance-sheet-statement",
}

for file_name, endpoint in endpoints.items():
    url = f"{BASE_URL}/{endpoint}"
    params = {
        "symbol": SYMBOL,
        "limit": 5,
        "apikey": API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or not data:
            print(f"No data received for {file_name}.")
            continue

        df = pd.DataFrame(data)
        output_file = f"data/{file_name}.csv"
        df.to_csv(output_file, index=False)

        print(f"{file_name}: {len(df)} records saved to {output_file}")

    except requests.exceptions.RequestException as error:
        print(f"Request failed for {file_name}: {error}")

print("Financial data download process completed.")
# Check the downloaded cash flow data
df = pd.read_csv("data/cash_flow.csv")

print("\n--- First 5 Rows ---")
print(df.head())

print("\n--- Dataset Shape ---")
print(df.shape)

print("\n--- Column Names ---")
print(df.columns.tolist())

print("\n--- Missing Values ---")
print(df.isnull().sum())

# Select important financial columns
columns_to_analyze = [
    "date",
    "netIncome",
    "operatingCashFlow",
    "capitalExpenditure",
    "freeCashFlow"
]

financial_summary = df[columns_to_analyze].copy()

print("\n--- Financial Summary ---")
print(financial_summary)

print("\n--- Average Financial Metrics ---")
print(financial_summary[
    ["netIncome", "operatingCashFlow", "capitalExpenditure", "freeCashFlow"]
].mean())


# Calculate Cash Flow Margin

financial_summary["cashFlowMargin"] = (
    financial_summary["freeCashFlow"]
    / financial_summary["netIncome"]
) * 100

print("\n--- Cash Flow Margin (%) ---")
print(
    financial_summary[
        ["date", "netIncome", "freeCashFlow", "cashFlowMargin"]
    ].round(2)
)



# Financial Trend Analysis

financial_summary["date"] = pd.to_datetime(
    financial_summary["date"]
)

financial_summary = financial_summary.sort_values("date")

print("\n--- Financial Trend Analysis ---")

print(
    financial_summary[
        ["date", "netIncome", "freeCashFlow"]
    ].to_string(index=False)
)

financial_summary["FCF_Change_Percentage"] = (
    financial_summary["freeCashFlow"].pct_change() * 100
)

print("\n--- Yearly Free Cash Flow Change (%) ---")


print(
    financial_summary[
        ["date", "freeCashFlow", "FCF_Change_Percentage"]
    ].to_string(index=False, formatters={
        "FCF_Change_Percentage": lambda x: (
            "N/A" if pd.isna(x) else f"{x:.2f}"
        )
    })
)
# Free Cash Flow Forecasting

financial_summary["Year"] = (
    financial_summary["date"].dt.year
)

X = financial_summary[["Year"]]
y = financial_summary["freeCashFlow"]

model = LinearRegression()
model.fit(X, y)

next_year = pd.DataFrame({"Year": [2026]})
forecast = model.predict(next_year)

print("\n--- Free Cash Flow Forecast ---")
print(f"Forecast Year: 2026")
print(f"Predicted Free Cash Flow: ${forecast[0]:,.2f}")
# Export financial analysis to Excel

with pd.ExcelWriter("outputs/Financial_Analysis.xlsx") as writer:
    financial_summary.to_excel(
        writer,
        sheet_name="Financial Summary",
        index=False
    )

    financial_summary[
        [
            "netIncome",
            "operatingCashFlow",
            "capitalExpenditure",
            "freeCashFlow"
        ]
    ].mean().reset_index().to_excel(
        writer,
        sheet_name="Average Metrics",
        index=False,
        header=["Metric", "Average Value"]
    )
    # Save forecast to Excel
    forecast_df = pd.DataFrame({
        "Year": [2026],
        "Predicted Free Cash Flow": [forecast[0]]
    })

    forecast_df.to_excel(
        writer,
        sheet_name="Forecast",
        index=False
    )
print("\nExcel report saved: outputs/Financial_Analysis.xlsx")
# Forecast Accuracy Check: Predict 2025 using 2021-2024 data

train_data = financial_summary[
    financial_summary["Year"] < 2025
]

test_data = financial_summary[
    financial_summary["Year"] == 2025
]

X_train = train_data[["Year"]]
y_train = train_data["freeCashFlow"]

X_test = test_data[["Year"]]
y_test = test_data["freeCashFlow"]

test_model = LinearRegression()
test_model.fit(X_train, y_train)

predicted_2025 = test_model.predict(X_test)[0]
actual_2025 = y_test.iloc[0]

error = abs(actual_2025 - predicted_2025)
percentage_error = (error / abs(actual_2025)) * 100

print("\n--- Forecast Accuracy Check ---")
print(f"Actual 2025 FCF: ${actual_2025:,.2f}")
print(f"Predicted 2025 FCF: ${predicted_2025:,.2f}")
print(f"Absolute Error: ${error:,.2f}")
print(f"Absolute Percentage Error: {percentage_error:.2f}%")
# Save Forecast Accuracy to Excel

accuracy_df = pd.DataFrame({
    "Metric": [
        "Forecast Year",
        "Actual Free Cash Flow",
        "Predicted Free Cash Flow",
        "Absolute Error",
        "Absolute Percentage Error"
    ],
    "Value": [
        2025,
        actual_2025,
        predicted_2025,
        error,
        percentage_error
    ]
})

with pd.ExcelWriter(
    "outputs/Financial_Analysis.xlsx",
    mode="a",
    engine="openpyxl",
    if_sheet_exists="replace"
) as writer:
    accuracy_df.to_excel(
        writer,
        sheet_name="Forecast Accuracy",
        index=False
    )

print("Forecast Accuracy saved to Excel successfully!")