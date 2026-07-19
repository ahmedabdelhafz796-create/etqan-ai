"""Ch4: full feature engineering pipeline on real GOOG data."""
import pandas as pd
from backtesting.test import GOOG

df = GOOG.copy()
df["ret1"] = df.Close.pct_change()
for k in (1, 2, 3, 5, 10):
    df[f"ret_lag{k}"] = df["ret1"].shift(k)
df["ma20"] = df.Close.rolling(20).mean()
df["dist_ma20"] = df.Close / df["ma20"] - 1
delta = df.Close.diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = (-delta.clip(upper=0)).rolling(14).mean()
df["rsi14"] = 100 - 100 / (1 + gain / loss)
df["vol20"] = df["ret1"].rolling(20).std()
df["target"] = (df.Close.shift(-1) > df.Close).astype(int)
df = df.dropna()
n = len(df)
train, val, test = df.iloc[:int(n*.7)], df.iloc[int(n*.7):int(n*.85)], df.iloc[int(n*.85):]
print(f"rows: train={len(train)} val={len(val)} test={len(test)}")
print(df[["ret1", "dist_ma20", "rsi14", "vol20", "target"]].tail(3))
