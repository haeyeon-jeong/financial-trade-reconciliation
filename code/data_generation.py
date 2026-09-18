"""
Run this script to generate your project dataset.
"""

import pandas as pd
import numpy as np
import random
from datetime import timedelta
import os

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

os.makedirs("data", exist_ok=True)

symbols = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'SPY', 'META', 'GOOGL', 'XOM', 'JPM']
accounts = ['ACC1', 'ACC2', 'ACC3'] 
venues = ['NYSE', 'NASDAQ', 'ARCA', 'BATS']
trade_types = ['REG', 'MOC', 'MOO', 'VWAP']

start_date = pd.to_datetime('2023-03-01')
end_date = pd.to_datetime('2023-03-10')
dates = pd.date_range(start_date, end_date)
num_trades = random.randint(250, 400) 

trade_ids = [f"T{100000 + i}" for i in range(num_trades)]

df_trades = pd.DataFrame({
    'trade_id': trade_ids,
    'symbol': np.random.choice(symbols, num_trades),
    'account': np.random.choice(accounts, num_trades),
    'trade_date': np.random.choice(dates, num_trades),
    'side': np.random.choice(['BUY', 'SELL'], num_trades),
    'quantity': np.random.randint(10, 5000, num_trades),
    'price': np.round(np.random.uniform(20, 1000, num_trades), 2),
    'venue': np.random.choice(venues, num_trades),
    'trade_type': np.random.choice(trade_types, num_trades),
})

df_trades['signed_qty'] = df_trades['quantity'] * np.where(df_trades['side'] == 'BUY', 1, -1)
df_trades['notional'] = df_trades['quantity'] * df_trades['price']
df_trades['fee'] = np.round(df_trades['notional'] * np.random.uniform(0.00005, 0.0005), 2)

df_trades['settlement_date'] = df_trades['trade_date'] + pd.to_timedelta(1, unit="D")

zero_qty_indices = np.random.choice(df_trades.index, 6, replace=False)
df_trades.loc[zero_qty_indices, 'quantity'] = 0
df_trades.loc[zero_qty_indices, 'signed_qty'] = 0
df_trades.loc[zero_qty_indices, 'notional'] = 0

neg_qty_indices = np.random.choice(df_trades.index.difference(zero_qty_indices), 6, replace=False)
df_trades.loc[neg_qty_indices, 'quantity'] *= -1 
dup_indices = np.random.choice(df_trades.index, 8, replace=False)
dups = df_trades.loc[dup_indices].copy()
dups['quantity'] = dups['quantity'] + np.random.randint(-50, 50, len(dups))
dups['price'] = np.round(dups['price'] * np.random.uniform(0.98, 1.02, len(dups)), 2)
df_trades = pd.concat([df_trades, dups], ignore_index=True)
outlier_indices = np.random.choice(df_trades.index, 6, replace=False)
df_trades.loc[outlier_indices, 'price'] *= np.random.choice([0.01, 10, 25])  # huge spike or crash
df_trades['notional'] = df_trades['quantity'].abs() * df_trades['price']
bad_settle_indices = np.random.choice(df_trades.index, 6, replace=False)
df_trades.loc[bad_settle_indices, 'settlement_date'] = df_trades.loc[bad_settle_indices, 'trade_date'] - pd.to_timedelta(
    np.random.randint(0, 2), unit="D"
)
nan_price_indices = np.random.choice(df_trades.index, 4, replace=False)
df_trades.loc[nan_price_indices, 'price'] = np.nan
df_trades.loc[nan_price_indices, 'notional'] = np.nan
nan_venue_indices = np.random.choice(df_trades.index, 4, replace=False)
df_trades.loc[nan_venue_indices, 'venue'] = None
df_trades = df_trades.sort_values(['trade_date', 'symbol', 'account']).reset_index(drop=True)
df_trades.to_csv("data/sample_trades.csv", index=False)
pos_rows = []
for sym in symbols:
    for acc in accounts:
        pos_rows.append({
            'symbol': sym,
            'account': acc,
            'position_t0': np.random.randint(1000, 10000)
        })
df_positions_t0 = pd.DataFrame(pos_rows)
net_trades = (
    df_trades
    .groupby(['symbol', 'account'])['signed_qty']
    .sum()
    .reset_index()
    .rename(columns={'signed_qty': 'net_qty'})
)
df_positions_t1 = df_positions_t0.merge(net_trades, on=['symbol', 'account'], how='left')
df_positions_t1['net_qty'] = df_positions_t1['net_qty'].fillna(0)
df_positions_t1['position_t1'] = df_positions_t1['position_t0'] + df_positions_t1['net_qty']
drift_idx = df_positions_t1.sample(1).index
df_positions_t1.loc[drift_idx, 'position_t1'] += random.choice([250, -400, 600])
missing_pos_row = df_positions_t1.sample(1)
df_positions_t1 = df_positions_t1.drop(missing_pos_row.index)
bogus_symbol = "ZZZZ" 
df_positions_t0 = pd.concat([
    df_positions_t0,
    pd.DataFrame([{'symbol': bogus_symbol, 'account': 'ACC1', 'position_t0': 0}])
], ignore_index=True)
df_positions_t1 = pd.concat([
    df_positions_t1,
    pd.DataFrame([{'symbol': bogus_symbol, 'account': 'ACC1', 'net_qty': 0, 'position_t1': 500}])
], ignore_index=True)
df_positions_t0 = df_positions_t0[['symbol', 'account', 'position_t0']]
df_positions_t1 = df_positions_t1[['symbol', 'account', 'position_t1']]
df_positions_t0.to_csv("data/positions_t0.csv", index=False)
df_positions_t1.to_csv("data/positions_t1.csv", index=False)
corp_rows = []
for sym in symbols:
    corp_rows.append({
        'symbol': sym,
        'ex_date': np.random.choice(dates),
        'corp_type': random.choice(['DIV', 'SPLIT', 'NONE']),
        'corp_shares': random.choice([0, 0, 0, 50, 100, None]) 
    })

df_corp = pd.DataFrame(corp_rows)
problem_ca_symbol = random.choice(symbols)
df_corp.loc[df_corp['symbol'] == problem_ca_symbol, 'corp_shares'] = random.choice([300, -150])
drop_ca_symbol = random.choice([s for s in symbols if s != problem_ca_symbol])
df_corp = df_corp[df_corp['symbol'] != drop_ca_symbol]

df_corp.to_csv("data/corp_actions.csv", index=False)

