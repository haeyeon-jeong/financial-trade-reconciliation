# Financial Trade Reconciliation & Analytics

## Overview
This project uses Python to clean and analyze financial trade data, generate daily and symbol-level reports, and reconcile position changes against trading activity and corporate actions.

The project uses synthetic financial data generated with an instructor-provided Python script.  
The dataset includes intentionally introduced data quality issues.  

The goal is to identify discrepancies, investigate missing records, and present the results through a Streamlit dashboard.

---

## Authors
Haeyeon Jeong 

---

## Dataset
Four datasets were used:

| Dataset | Records | Description |
|---|---:|---|
| Trades | 286 | Trading activity across symbols and accounts |
| Positions T0 | 31 | Starting positions |
| Positions T1 | 30 | Ending positions |
| Corporate Actions | 9 | Corporate action adjustments |

---

## Methodology

**1. Data Quality Assessment & Cleaning**

Checked for duplicate trade IDs, invalid quantities, missing prices and venues, settlement date issues, and unusual trade prices.

- Removed 33 invalid or duplicate trade records.
- Retained 253 cleaned trades.
- Flagged 15 potential price outliers for review without removing them.
- Identified missing position records and incomplete corporate action data.
  

**2. Trade Aggregation & Reporting**

Generated daily and symbol-level reports covering:

- Trading volume and net trade quantity
- Trade counts and notional values
- Average trade prices

Validated the aggregated results against cleaned trade quantities.  


**3. Position Reconciliation**

Compared actual position changes with expected changes from net trades and corporate action adjustments.

**Actual Change = Position T1 − Position T0**

**Expected Change = Net Trade Quantity + Corporate Action Shares**

**Reconciliation Difference = Actual Change − Expected Change**

Results were classified as MATCH, MISMATCH, or INVALID.

Incomplete account-symbol position records were excluded from reconciliation, while missing corporate action share values were flagged as INVALID.  


**4. Dashboard & Visualization**

Built a Streamlit dashboard to display:

- Trading volume by symbol
- Overall and individual symbol price trends
- Reconciliation status
- Reconciliation differences
- Detailed reconciliation results

---

## Key Findings

- AAPL had the highest trading volume with 88,307 shares.
- META had the largest positive net quantity (+31,813 shares).
- MSFT had the largest negative net quantity (−8,691 shares).
- Of 10 symbols, 1 MATCHED, 8 MISMATCHED, and 1 was INVALID.

---

## Project Structure

```
financial-trade-reconciliation/
│
├── data/                         # Synthetic financial datasets
│   ├── sample_trades.csv         # Trade transactions across symbols and accounts
│   ├── positions_t0.csv          # Starting positions by account and symbol
│   ├── positions_t1.csv          # Ending positions by account and symbol
│   └── corp_actions.csv          # Corporate action records and share adjustments
│
├── code/                         # Data processing and analysis scripts
│   ├── data_generation.py        # Generates synthetic financial datasets
│   ├── reconciliation.py         # Data cleaning, validation, reporting, and reconciliation
│   └── reconciliation.ipynb      # Jupyter Notebook with analysis and outputs
│
├── reports/                      # Generated reports and visualizations
│   ├── cleaned_trades.csv        # Cleaned and validated trade data
│   ├── daily_report.csv          # Daily trading summary by symbol
│   ├── symbol_report.csv         # Aggregated trading statistics by symbol
│   ├── full_reconciliation.csv   # Position reconciliation results and status
│   └── *.png                     # Trading volume, price trends, and reconciliation charts
│
├── presentation/                 # Final project presentation (PDF)
├── app.py                        # Streamlit dashboard for interactive analysis
└── README.md                     # Project overview, methodology, and findings

```
---
## How to Run
**Install the required Python packages:**

`pip install pandas numpy matplotlib seaborn streamlit`


**From the project root directory, run:**

`python code/reconciliation.py`  
`streamlit run app.py`

The reconciliation script generates cleaned data, reports, and charts in the reports/ folder.  
The Streamlit app uses these outputs to display the dashboard.

---

## Limitations
- The dataset was simulated using an instructor-provided Python script.
- Corporate action records did not include account information, limiting account-level reconciliation.
- Reconciliation results were not verified against real trading records.

---

## Tools
Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit
