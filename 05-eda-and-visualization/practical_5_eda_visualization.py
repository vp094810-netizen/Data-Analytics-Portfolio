
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

sns.set_theme(style="whitegrid")

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 30)

FILE_PATH = None
DATE_COLUMN = "order_date"
GROUP_COLUMN = "region"
TARGET_COLUMN = "sales"


# --------------------------------------------------
# STEP 1: CREATE SAMPLE DATA
# --------------------------------------------------

def make_sample_data(n=600, seed=42):

    rng = np.random.default_rng(seed)

    dates = pd.date_range(
        start="2023-01-01",
        periods=n,
        freq="D"
    )

    sales = (
        np.linspace(100, 200, n)
        + 15 * np.sin(np.arange(n) / 30)
        + rng.normal(0, 12, n)
    )

    # Add outliers
    sales[rng.choice(n, 6, replace=False)] *= 2.5

    data = pd.DataFrame({
        "order_date": dates,
        "sales": sales,
        "units": rng.poisson(25, n),
        "price": rng.normal(50, 7, n),
        "region": rng.choice(
            ["North", "South", "East", "West"],
            n,
            p=[0.35, 0.25, 0.25, 0.15]
        )
    })

    # Add missing values
    missing_rows = rng.choice(n, 25, replace=False)
    data.loc[missing_rows, "price"] = np.nan

    return data


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("===== LOADING DATA =====")

if FILE_PATH is None:

    df = make_sample_data()
    print("Sample dataset created.")

else:

    try:
        if FILE_PATH.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(FILE_PATH)
        else:
            df = pd.read_csv(FILE_PATH)

        print("Dataset loaded successfully.")

    except Exception as e:
        print("Error loading file:", e)
        raise SystemExit


if df.empty:
    print("Dataset is empty.")
    raise SystemExit


# Convert date column
if DATE_COLUMN in df.columns:

    df[DATE_COLUMN] = pd.to_datetime(
        df[DATE_COLUMN],
        errors="coerce"
    )


# Check required target column
if TARGET_COLUMN not in df.columns:
    print(f"Error: '{TARGET_COLUMN}' column not found.")
    print("Available columns:", df.columns.tolist())
    raise SystemExit


# --------------------------------------------------
# STEP 2: FIRST LOOK AT DATA
# --------------------------------------------------

print("\n===== STEP 2: FIRST LOOK AT DATA =====")

print("\nDataset shape:", df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nLast 5 rows:")
print(df.tail())

print("\nData types:")
print(df.dtypes)

print("\nDataset information:")
df.info()


# Identify numeric and categorical columns
num_cols = df.select_dtypes(
    include="number"
).columns.tolist()

cat_cols = [
    col for col in df.columns
    if col not in num_cols
    and not pd.api.types.is_datetime64_any_dtype(df[col])
]

print("\nNumeric columns:", num_cols)
print("Categorical columns:", cat_cols)


# --------------------------------------------------
# STEP 3: DATA QUALITY
# --------------------------------------------------

print("\n===== STEP 3: DATA QUALITY =====")

print("\nMissing values in each column:")
print(df.isnull().sum())

print("\nTotal missing values:", df.isnull().sum().sum())

print("\nDuplicate rows:", df.duplicated().sum())


# --------------------------------------------------
# STEP 4: DESCRIPTIVE STATISTICS
# --------------------------------------------------

print("\n===== STEP 4: DESCRIPTIVE STATISTICS =====")

if num_cols:

    summary = df[num_cols].describe().T

    summary["median"] = df[num_cols].median()
    summary["variance"] = df[num_cols].var()
    summary["IQR"] = summary["75%"] - summary["25%"]
    summary["skewness"] = df[num_cols].skew()

    print(summary.round(2))

    # Distribution shape
    print("\nDistribution shape:")

    for col in num_cols:

        sk = summary.loc[col, "skewness"]

        if pd.isna(sk):
            shape = "Cannot determine"

        elif sk > 0.5:
            shape = "Right-skewed"

        elif sk < -0.5:
            shape = "Left-skewed"

        else:
            shape = "Roughly symmetric"

        print(f"{col}: {shape}")

else:
    print("No numeric columns found.")


# Frequency counts for categorical columns
for col in cat_cols:

    print(f"\nFrequency counts for {col}:")
    print(df[col].value_counts(dropna=False))


# --------------------------------------------------
# STEP 5: DISTRIBUTION ANALYSIS
# --------------------------------------------------

print("\n===== STEP 5: DISTRIBUTION ANALYSIS =====")

sales_data = pd.to_numeric(
    df[TARGET_COLUMN],
    errors="coerce"
).dropna()

if not sales_data.empty:

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Histogram
    sns.histplot(
        sales_data,
        kde=True,
        ax=axes[0]
    )

    axes[0].axvline(
        sales_data.mean(),
        linestyle="--",
        label="Mean"
    )

    axes[0].axvline(
        sales_data.median(),
        linestyle="-.",
        label="Median"
    )

    axes[0].set_title(f"Histogram of {TARGET_COLUMN}")
    axes[0].legend()

    # Boxplot
    sns.boxplot(
        x=sales_data,
        ax=axes[1]
    )

    axes[1].set_title(f"Boxplot of {TARGET_COLUMN}")

    plt.tight_layout()
    plt.savefig("step5_distribution.png", dpi=120)
    plt.show()

    print("Chart saved: step5_distribution.png")

else:
    print("No valid numeric target values to plot.")


# --------------------------------------------------
# STEP 6: OUTLIER DETECTION USING IQR
# --------------------------------------------------

print("\n===== STEP 6: OUTLIER DETECTION =====")

for col in num_cols:

    values = df[col].dropna()

    if values.empty:
        print(f"{col}: No valid values.")
        continue

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr

    count = ((values < low) | (values > high)).sum()

    print(
        f"{col}: Lower = {low:.2f}, "
        f"Upper = {high:.2f}, Outliers = {count}"
    )


# Display target column outliers
if not sales_data.empty:

    q1 = sales_data.quantile(0.25)
    q3 = sales_data.quantile(0.75)
    iqr = q3 - q1

    outliers = df.loc[
        sales_data.index[
            (sales_data < q1 - 1.5 * iqr)
            | (sales_data > q3 + 1.5 * iqr)
        ]
    ]

    print(f"\nOutlier rows in {TARGET_COLUMN}:")
    print(outliers.head(10))

    print("Total target outlier rows:", len(outliers))


# --------------------------------------------------
# STEP 7: CORRELATION ANALYSIS
# --------------------------------------------------

print("\n===== STEP 7: CORRELATION ANALYSIS =====")

if len(num_cols) >= 2:

    corr = df[num_cols].corr()

    print(corr.round(2))

    plt.figure(figsize=(8, 6))

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1
    )

    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("step7_correlation.png", dpi=120)
    plt.show()

    print("Chart saved: step7_correlation.png")

else:
    print("At least two numeric columns are needed for correlation.")


# --------------------------------------------------
# STEP 8: GROUP ANALYSIS
# --------------------------------------------------

print("\n===== STEP 8: GROUP ANALYSIS =====")

if GROUP_COLUMN in df.columns:

    group_data = df[[GROUP_COLUMN, TARGET_COLUMN]].copy()

    group_data[TARGET_COLUMN] = pd.to_numeric(
        group_data[TARGET_COLUMN],
        errors="coerce"
    )

    group_data = group_data.dropna(
        subset=[GROUP_COLUMN, TARGET_COLUMN]
    )

    if not group_data.empty:

        group_summary = (
            group_data.groupby(GROUP_COLUMN)[TARGET_COLUMN]
            .agg([
                "count",
                "mean",
                "median",
                "std",
                "min",
                "max"
            ])
            .round(2)
        )

        print(f"\n{TARGET_COLUMN} by {GROUP_COLUMN}:")
        print(group_summary)

        plt.figure(figsize=(8, 5))

        sns.boxplot(
            data=group_data,
            x=GROUP_COLUMN,
            y=TARGET_COLUMN
        )

        plt.title(f"{TARGET_COLUMN} by {GROUP_COLUMN}")
        plt.tight_layout()
        plt.savefig("step8_groups.png", dpi=120)
        plt.show()

        print("Chart saved: step8_groups.png")

    else:
        print("No valid data for group analysis.")

else:
    print(f"Column '{GROUP_COLUMN}' not found.")


# --------------------------------------------------
# STEP 9: TIME TREND ANALYSIS
# --------------------------------------------------

print("\n===== STEP 9: TIME TREND ANALYSIS =====")

if DATE_COLUMN in df.columns:

    time_data = df[[DATE_COLUMN, TARGET_COLUMN]].copy()

    time_data[TARGET_COLUMN] = pd.to_numeric(
        time_data[TARGET_COLUMN],
        errors="coerce"
    )

    time_data = time_data.dropna(
        subset=[DATE_COLUMN, TARGET_COLUMN]
    )

    if not time_data.empty:

        monthly = (
            time_data.set_index(DATE_COLUMN)[TARGET_COLUMN]
            .resample("MS")
            .mean()
            .dropna()
        )

        if len(monthly) >= 2:

            rolling = monthly.rolling(
                window=3,
                min_periods=1
            ).mean()

            x = np.arange(len(monthly))

            slope, intercept = np.polyfit(
                x,
                monthly.to_numpy(),
                1
            )

            r_squared = np.corrcoef(
                x,
                monthly.to_numpy()
            )[0, 1] ** 2

            direction = (
                "UPWARD" if slope > 0
                else "DOWNWARD" if slope < 0
                else "FLAT"
            )

            print("Trend direction:", direction)
            print(f"Slope per month: {slope:.2f}")
            print(f"R-squared: {r_squared:.2f}")

            plt.figure(figsize=(10, 5))

            plt.plot(
                monthly.index,
                monthly.values,
                marker="o",
                label="Monthly Average"
            )

            plt.plot(
                monthly.index,
                rolling.values,
                linewidth=2,
                label="3-Month Rolling Average"
            )

            plt.plot(
                monthly.index,
                intercept + slope * x,
                "r--",
                label="Trend Line"
            )

            plt.title(f"Monthly Trend of {TARGET_COLUMN}")
            plt.xlabel("Month")
            plt.ylabel(TARGET_COLUMN)
            plt.legend()
            plt.tight_layout()
            plt.savefig("step9_trend.png", dpi=120)
            plt.show()

            print("Chart saved: step9_trend.png")

        else:
            print("At least two months of valid data are needed.")

    else:
        print("No valid date and target values for trend analysis.")

else:
    print(f"Date column '{DATE_COLUMN}' not found.")


# --------------------------------------------------
# END OF PROGRAM
# --------------------------------------------------

print("\n===== EDA COMPLETED SUCCESSFULLY =====")
