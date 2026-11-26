from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "sales_database.csv"
CHART_PATH = BASE_DIR / "sales_dynamics.png"


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    required_columns = {
        "Product",
        "Price",
        "Quantity_Delivered",
        "Quantity_Sold",
        "Remaining",
        "Revenue",
    }
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    missing_values = int(data.isna().sum().sum())
    duplicate_rows = int(data.duplicated().sum())
    duplicate_products = int(data["Product"].duplicated().sum())
    data["Revenue"] = data["Price"] * data["Quantity_Sold"]
    prices = data["Price"].dropna()
    q1 = prices.quantile(0.25)
    q3 = prices.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = prices[(prices < lower_bound) | (prices > upper_bound)]

    print(f"Rows: {len(data)}")
    print(f"Missing values: {missing_values}")
    print(f"Duplicate rows: {duplicate_rows}")
    print(f"Duplicate products: {duplicate_products}")
    print(f"Mean price: {prices.mean():.2f}")
    print(f"Median price: {prices.median():.2f}")
    print(f"Price outliers (IQR bounds {lower_bound:.2f}..{upper_bound:.2f}):")
    print(outliers.to_string())
    if not outliers.empty:
        regular_prices = prices[~prices.index.isin(outliers.index)]
        print(f"Mean price without outliers: {regular_prices.mean():.2f}")
        print(f"Median price without outliers: {regular_prices.median():.2f}")
    print(f"Corrected total revenue: {data['Revenue'].sum():.2f}")

    if "Date" in data.columns and data["Date"].notna().any():
        data["Date"] = pd.to_datetime(data["Date"], errors="raise")
        daily_revenue = data.groupby("Date")["Revenue"].sum().sort_index()
        daily_revenue.plot(marker="o")
        plt.xlabel("Date")
        plt.ylabel("Revenue")
        plt.title("Revenue by date")
        plt.xticks(rotation=45)
        print(f"Revenue dates: {daily_revenue.index.min().date()} to "
              f"{daily_revenue.index.max().date()}")
    else:
        data.groupby("Product")["Revenue"].sum().sort_values().plot(
            kind="bar", color="steelblue"
        )
        plt.xlabel("Product")
        plt.ylabel("Revenue")
        plt.title("Revenue by product (dates not available)")
        plt.xticks(rotation=30, ha="right")
        print("Date chart unavailable: the source data has no Date column.")

    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=160)
    plt.close()
    print(f"Chart saved to: {CHART_PATH.name}")


if __name__ == "__main__":
    main()
