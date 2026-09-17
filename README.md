# Financial Trade Reconciliation & Analytics

## Overview
This project explores financial trade data using SQL and Python, focusing on data cleaning, trade analysis, and position reconciliation.

The project uses synthetically generated trade, position, and corporate-action data with intentionally added data-quality issues. SQL is used to query and analyze the data, while Python is used for cleaning, reconciliation, and further analysis.

The goal is to demonstrate a practical workflow for working with financial transaction data and identifying discrepancies between trading activity and daily positions.

---

## Authors
Haeyeon Jeong 

---

## Data
The project uses synthetically generated financial data for analysis and testing.

The datasets include:
- Trade data
- T0 (starting) positions
- T1 (ending) positions
- Corporate actions

The data includes intentionally generated issues such as duplicate trades, invalid quantities, missing values, settlement-date errors, missing position records, and corporate-action errors.

---

## Methodology

**1. Data Validation & Cleaning**

Trade data was inspected and cleaned before analysis. Key issues included:
- Duplicate trade IDs
- Zero and negative quantities
- Missing prices
- Missing venues
- Invalid settlement dates
- Price anomalies

**2. Trade Analysis & Reporting**

Cleaned trade data was analyzed to summarize:

- Trading volume by symbol
- Net trade quantity
- Average prices
- Daily trading activity

**3. Position Reconciliation**

Position changes were compared with trading activity and corporate actions.

Actual Position Change = Position T1 − Position T0

Expected Position Change = Net Trade Quantity + Corporate Action Shares

Reconciliation Difference = Actual Change − Expected Change

A difference of zero indicates a match, while a non-zero difference indicates a reconciliation issue.

**4. Visualization & Insights**

Charts were created to summarize key results, including trading volume, price movement, and reconciliation status.

---

## Key Findings

- AAPL had the highest total trading volume with 88,307 shares.
- META had the largest positive net quantity at +31,813 shares.
- MSFT had the largest negative net quantity at −8,691 shares.
- Only 1 of 11 symbols reconciled correctly.
- Missing position records and incomplete corporate-action data contributed to reconciliation discrepancies.

---

## Project Structure

financial-trade-reconciliation/
│
├── data/                 # Generated trade, position, and corporate-action data
├── code/
│   ├── final_project.py     # Generates the synthetic financial datasets
│   └── final_project_hy.py  # Data cleaning, analysis, reconciliation, and visualization
├── reports/              # Cleaned data, analytical reports, and charts
├── presentation/         # Final project presentation
└── README.md

---

## Tools
Python, Pandas, SQL, Matplotlib
