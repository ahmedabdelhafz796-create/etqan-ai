"""Ch1: first ML idea on real GOOG data (actual result ~54%)."""
import numpy as np
from backtesting.test import GOOG
from sklearn.linear_model import LogisticRegression

closes = GOOG.Close.values
returns = np.diff(closes) / closes[:-1]
X = returns[:-1].reshape(-1, 1)
y = (returns[1:] > 0).astype(int)
split = int(len(X) * 0.8)
model = LogisticRegression().fit(X[:split], y[:split])
print(f"Accuracy on unseen future: {model.score(X[split:], y[split:]):.1%}")
