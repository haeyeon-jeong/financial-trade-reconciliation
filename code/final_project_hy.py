#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create reports folder
os.makedirs("reports", exist_ok=True)


# Part 1 Load Data
# Load datasets
df_trades = pd.read_csv("data/sample_trades.csv")
df_t0 = pd.read_csv("data/positions_t0.csv")
df_t1 = pd.read_csv("data/positions_t1.csv")
df_corp = pd.read_csv("data/corp_actions.csv")

# Convert date columns
df_trades["trade_date"] = pd.to_datetime(
    df_trades["trade_date"], errors="coerce"
)

df_trades["settlement_date"] = pd.to_datetime(
    df_trades["settlement_date"], errors="coerce"
)

df_corp["ex_date"] = pd.to_datetime(
    df_corp["ex_date"], errors="coerce"
)

print("Trades:", df_trades.shape)
print("Positions T0:", df_t0.shape)
print("Positions T1:", df_t1.shape)
print("Corporate Actions:", df_corp.shape)


# Part 2 Initial Data Inspection
# Data Summary Before Cleaning
print("TRADE DATA SUMMARY")
print("----------------------")

print("Total rows before cleaning:", len(df_trades))

print("\nNull values per column:")
print(df_trades.isna().sum())

print("\nDuplicate trade IDs:")
print(df_trades.duplicated(subset=["trade_id"]).sum())

print("\nZero quantity trades:")
print((df_trades["quantity"] == 0).sum())

print("\nNegative quantity trades:")
print((df_trades["quantity"] < 0).sum())

print("\nSettlement date issues:")
print((df_trades["settlement_date"] <= df_trades["trade_date"]).sum())


# Part 3 Detect the Issues
# 1) Zero quantity trades
zero_qty = df_trades[df_trades["quantity"] == 0]

print("\nZero quantity trades:")
print(zero_qty)


# 2) Negative quantity trades
negative_qty = df_trades[df_trades["quantity"] < 0]

print("\nNegative quantity trades:")
print(negative_qty)


# 3) Duplicate trade IDs
duplicate_trades = df_trades[
    df_trades.duplicated(
        subset=["trade_id"],
        keep=False
    )
]

print("\nDuplicate trade IDs:")
print(duplicate_trades.sort_values("trade_id"))


# 4) Missing price
missing_price = df_trades[
    df_trades["price"].isna()
]

print("\nMissing price:")
print(missing_price)


# 5) Missing venue
missing_venue = df_trades[
    df_trades["venue"].isna()
]

print("\nMissing venue:")
print(missing_venue)


# 6) Settlement date issues
bad_settlement = df_trades[
    df_trades["settlement_date"]
    <= df_trades["trade_date"]
]

print("\nSettlement date issues:")
print(bad_settlement)

# 7) Detect price spikes / drops
# unusual 0.01x / 10x / 25x style price changes.
# Use each symbol's median price as a simple reference.
median_price = (
    df_trades
    .groupby("symbol")["price"]
    .transform("median")
)

price_ratio = (
    df_trades["price"]
    / median_price
)

price_outliers = df_trades[
    (price_ratio < 0.1)
    | (price_ratio > 5)
]

print("\nPossible price spikes/drops:")
print(
    price_outliers[
        [
            "trade_id",
            "symbol",
            "price"
        ]
    ]
)

# 8) Check missing position rows
position_check = df_t0.merge(
    df_t1,
    on=["symbol", "account"],
    how="outer",
    indicator=True
)

missing_positions = position_check[
    position_check["_merge"] != "both"
]

print("\nMissing position rows:")
print(missing_positions)

# 9) Check symbols that exist in positions but not trades
trade_symbols = set(df_trades["symbol"])

position_symbols = (
    set(df_t0["symbol"]) |
    set(df_t1["symbol"])
)

bogus_symbols = position_symbols - trade_symbols

print("\nPosition symbols not found in trades:")
print(bogus_symbols)

# 10) Check missing corporate action shares
missing_corp_shares = df_corp[
    df_corp["corp_shares"].isna()
]

print("\nMissing corporate action shares:")
print(missing_corp_shares)


# 11) Check symbols missing from corporate actions
corp_symbols = set(df_corp["symbol"])

missing_corp_symbols = trade_symbols - corp_symbols

print("\nSymbols missing from corporate actions:")
print(missing_corp_symbols)


# 12) Corporate action rows marked NONE
# but still containing shares
corp_none_with_shares = df_corp[
    (df_corp["corp_type"] == "NONE")
    & (df_corp["corp_shares"] != 0)
]

print("\nNONE corporate actions with non-zero shares:")
print(corp_none_with_shares)


# Part 4 Clean Data
# Create a copy before cleaning
df_clean = df_trades.copy()

print("CLEANING PROCESS")
print("----------------------")
print("Starting rows:", len(df_clean))

# 1) Remove zero and negative quantity trades
before = len(df_clean)

df_clean = df_clean[
    df_clean["quantity"] > 0
]

print("\n1. Zero/negative quantity trades")
print(
    "Rows deleted:",
    before - len(df_clean)
)
print(
    "Rows left:",
    len(df_clean)
)


# 2) Remove duplicate trade IDs
before = len(df_clean)

df_clean.drop_duplicates(
    subset=["trade_id"],
    keep="first",
    inplace=True
)

print("\n2. Duplicate trade IDs")
print(
    "Rows deleted:",
    before - len(df_clean)
)
print(
    "Rows left:",
    len(df_clean)
)


# 3) Remove rows with missing price
before = len(df_clean)

df_clean = df_clean[
    df_clean["price"].notna()
]

print("\n3. Missing price")
print(
    "Rows deleted:",
    before - len(df_clean)
)
print(
    "Rows left:",
    len(df_clean)
)

#  4) Remove rows with missing venue
before = len(df_clean)

df_clean = df_clean[
    df_clean["venue"].notna()
]

print("\n4. Missing venue")
print(
    "Rows deleted:",
    before - len(df_clean)
)
print(
    "Rows left:",
    len(df_clean)
)


# 5)Remove invalid settlement dates
before = len(df_clean)

df_clean = df_clean[
    df_clean["settlement_date"]
    > df_clean["trade_date"]
]

print("\n5. Settlement date issues")
print(
    "Rows deleted:",
    before - len(df_clean)
)
print(
    "Rows left:",
    len(df_clean)
)


# 6) Filter unrealistic price values
#
# This follows the simple rule used in the workshop.
# Sseparately detected relative price spikes above.

before = len(df_clean)

df_clean = df_clean[
    df_clean["price"].between(
        0.01,
        10000
    )
]

print("\n6. Unrealistic price values")
print(
    "Rows deleted:",
    before - len(df_clean)
)
print(
    "Rows left:",
    len(df_clean)
)


# Recalculate signed quantity after cleaning
df_clean["signed_qty"] = np.where(
    df_clean["side"] == "BUY",
    df_clean["quantity"],
    -df_clean["quantity"]
)



# Recalculate notional
df_clean["notional"] = (
    df_clean["quantity"]
    * df_clean["price"]
)

print(
    "\nRecalculated signed quantity and notional:"
)

print(
    df_clean[
        [
            "trade_id",
            "symbol",
            "side",
            "quantity",
            "signed_qty",
            "price",
            "notional"
        ]
    ].head(10)
)


print("\nCLEANING RESULT")
print("----------------------")

print(
    "Rows before cleaning:",
    len(df_trades)
)

print(
    "Rows after cleaning:",
    len(df_clean)
)

print(
    "Total rows deleted:",
    len(df_trades)
    - len(df_clean)
)



# Part 5 Validate Cleaning

print("DATA CLEANING SUMMARY")
print("----------------------")

print("Total rows before cleaning:", len(df_trades))
print("Total rows after cleaning:", len(df_clean))
print("Total rows deleted:", len(df_trades) - len(df_clean))

print("\nNull values per column:")
print(df_clean.isna().sum())

print("\nDuplicate trade IDs:")
print(df_clean.duplicated(subset=["trade_id"]).sum())

print("\nZero quantity trades:")
print((df_clean["quantity"] == 0).sum())

print("\nNegative quantity trades:")
print((df_clean["quantity"] < 0).sum())

print("\nSettlement date issues:")
print(
    (
        df_clean["settlement_date"]
        <= df_clean["trade_date"]
    ).sum()
)

print("\nInvalid price values:")
print(
    (~df_clean["price"].between(0.01, 10000)).sum()
)

print("\nMissing price:")
print(df_clean["price"].isna().sum())

print("\nMissing venue:")
print(df_clean["venue"].isna().sum())

# Save cleaned trade data
df_clean.to_csv(
    "reports/cleaned_trades.csv",
    index=False
)

print("\nSaved cleaned trade data.")

# Part 6 Reporting

# Daily summary by date and symbol
daily_report = (
    df_clean
    .groupby(["trade_date", "symbol"])
    .agg(
        trade_count=("trade_id", "count"),
        total_quantity=("quantity", "sum"),
        net_qty=("signed_qty", "sum"),
        total_notional=("notional", "sum"),
        avg_price=("price", "mean")
    )
    .reset_index()
)

print("DAILY REPORT")
print("----------------------")
print(daily_report.head(10))

# Save
daily_report.to_csv(
    "reports/daily_report.csv",
    index=False
)

print("\nSaved daily report.")

# Summary by symbol
symbol_report = (
    df_clean
    .groupby("symbol")
    .agg(
        trade_count=("trade_id", "count"),
        total_quantity=("quantity", "sum"),
        net_qty=("signed_qty", "sum"),
        total_notional=("notional", "sum"),
        avg_price=("price", "mean")
    )
    .reset_index()
)

print("\nSYMBOL REPORT")
print("----------------------")
print(
    symbol_report.sort_values(
        "total_quantity",
        ascending=False
    )
)

# Save
symbol_report.to_csv(
    "reports/symbol_report.csv",
    index=False
)


# Part 7 Reconciliation

# Aggregate cleaned trades by symbol
net_trades = (
    df_clean
    .groupby(
        "symbol",
        as_index=False
    )["signed_qty"]
    .sum()
    .rename(
        columns={
            "signed_qty":
            "net_qty"
        }
    )
)



print("\nNET TRADES BY SYMBOL")
print("----------------------")

print(net_trades)

# Aggregate T0 positions by symbol
positions_t0 = (
    df_t0
    .groupby(
        "symbol",
        as_index=False
    )["position_t0"]
    .sum()
)



# Aggregate T1 positions by symbol
positions_t1 = (
    df_t1
    .groupby(
        "symbol",
        as_index=False
    )["position_t1"]
    .sum()
)



print("\nPOSITIONS T0")
print("----------------------")
print(positions_t0)

print("\nPOSITIONS T1")
print("----------------------")
print(positions_t1)



# Merge T0 and T1
recon = positions_t0.merge(
    positions_t1,
    on="symbol",
    how="outer"
)



print("\nPOSITIONS AFTER MERGE")
print("----------------------")
print(recon)


# Merge net trades
recon = recon.merge(
    net_trades,
    on="symbol",
    how="left"
)


# No trade = 0 net quantity
recon["net_qty"] = (
    recon["net_qty"]
    .fillna(0)
)


# Merge corporate actions
recon = recon.merge(
    df_corp[
        [
            "symbol",
            "corp_shares"
        ]
    ],
    on="symbol",
    how="left"
)



# Flag missing corporate action data
recon["corp_action_missing"] = (
    recon["corp_shares"].isna()
)

print(
    "\nMissing corporate action shares:",
    recon["corp_shares"]
    .isna()
    .sum()
)



print(
    "\nSymbols with missing corporate action shares:"
)

print(
    recon.loc[
        recon["corp_action_missing"],
        [
            "symbol",
            "corp_shares"
        ]
    ]
)
# Fill missing corp shares with 0
# only for reconciliation calculation
recon["corp_shares"] = (
    recon["corp_shares"]
    .fillna(0)
)



print(
    "\nMissing corporate action shares after fill:",
    recon["corp_shares"]
    .isna()
    .sum()
)

# Reconciliation calculations

# Position change
recon["delta_pos"] = (
    recon["position_t1"]
    - recon["position_t0"]
)



# Expected position change
recon["expected_delta"] = (
    recon["net_qty"]
    + recon["corp_shares"]
)



# Reconciliation difference
recon["recon_diff"] = (
    recon["delta_pos"]
    - recon["expected_delta"]
)



print(
    "\nRECONCILIATION CALCULATIONS"
)

print("----------------------")

print(
    recon[
        [
            "symbol",
            "position_t0",
            "position_t1",
            "net_qty",
            "corp_shares",
            "delta_pos",
            "expected_delta",
            "recon_diff"
        ]
    ]
)

# Assign reconciliation status
recon["status"] = np.where(
    recon["recon_diff"] == 0,
    "MATCH",
    "MISMATCH"
)



print(
    "\nRECONCILIATION STATUS"
)

print("----------------------")

print(
    recon[
        [
            "symbol",
            "delta_pos",
            "expected_delta",
            "recon_diff",
            "status"
        ]
    ]
)



print("\nStatus count:")

print(
    recon["status"]
    .value_counts()
)

# Show mismatches
mismatches = recon[
    recon["status"] == "MISMATCH"
]


print(
    "\nRECONCILIATION MISMATCHES"
)

print("----------------------")

print(
    mismatches[
        [
            "symbol",
            "delta_pos",
            "expected_delta",
            "recon_diff",
            "corp_action_missing"
        ]
    ]
)

# Save reconciliation report
recon.to_csv(
    "reports/full_reconciliation.csv",
    index=False
)


print(
    "\nSaved full reconciliation report."
)

# Part 8 Visualization Dashboard

sns.set_style("whitegrid")


# ============================================================
# Chart 1
# Which symbols had the highest trading volume?
# ============================================================

volume_chart = (
    symbol_report
    .sort_values(
        "total_quantity",
        ascending=False
    )
)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=volume_chart,
    x="symbol",
    y="total_quantity"
)

plt.title(
    "Which symbols had the highest trading volume?"
)

plt.xlabel("Symbol")
plt.ylabel("Total Quantity")

plt.tight_layout()

plt.savefig(
    "reports/trading_volume.png"
)

plt.show()


# Insight
top_symbol = volume_chart.iloc[0]

print(
    "\nChart 1 Insight:",
    top_symbol["symbol"],
    "had the highest trading volume with",
    int(top_symbol["total_quantity"]),
    "shares."
)



# ============================================================
# Chart 2
# How did the price evolve over time?
# ============================================================

# Select the symbol with the highest trading volume
top_symbol_name = top_symbol["symbol"]

price_data = df_clean[
    df_clean["symbol"] == top_symbol_name
]

# Calculate average price by date
price_trend = (
    price_data
    .groupby("trade_date", as_index=False)["price"]
    .mean()
)


plt.figure(figsize=(10, 6))

sns.lineplot(
    data=price_trend,
    x="trade_date",
    y="price",
    marker="o"
)

plt.title(
    f"How did {top_symbol_name}'s price evolve over time?"
)

plt.xlabel("Trade Date")
plt.ylabel("Average Price")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "reports/price_trend.png"
)

plt.show()


# Insight
print(
    "\nChart 2 Insight:",
    top_symbol_name,
    "average price changed from",
    round(price_trend.iloc[0]["price"], 2),
    "to",
    round(price_trend.iloc[-1]["price"], 2),
    "during the period."
)



# ============================================================
# Chart 3
# What % of positions reconciled correctly?
# ============================================================

status_count = (
    recon["status"]
    .value_counts()
    .reset_index()
)

status_count.columns = [
    "status",
    "count"
]


# Calculate percentage
status_count["percentage"] = (
    status_count["count"]
    / status_count["count"].sum()
    * 100
)


plt.figure(figsize=(8, 6))

sns.barplot(
    data=status_count,
    x="status",
    y="percentage"
)

plt.title(
    "What % of positions reconciled correctly?"
)

plt.xlabel("Reconciliation Status")
plt.ylabel("Percentage (%)")

plt.tight_layout()

plt.savefig(
    "reports/reconciliation_status.png"
)

plt.show()


# Insight
match_percentage = status_count.loc[
    status_count["status"] == "MATCH",
    "percentage"
].iloc[0]

print(
    "\nChart 3 Insight:",
    round(match_percentage, 1),
    "% of positions reconciled correctly."
)