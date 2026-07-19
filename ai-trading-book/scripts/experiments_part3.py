# -*- coding: utf-8 -*-
"""Part 3 experiments (ch5-8) — ALL results computed on real data.
Saves figures + metrics.json with the real numbers quoted in the chapters."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figlib import NAVY, NAVY_DEEP, GOLD, GOLD_LIGHT, GREEN, RED, GREY, GRID, save, new_ax
from backtesting.test import GOOG, EURUSD

RESULTS = {}


def make_features(df):
    out = pd.DataFrame(index=df.index)
    c = df.Close
    out["ret1"] = c.pct_change()
    for k in (1, 2, 3, 5, 10):
        out[f"ret_lag{k}"] = out["ret1"].shift(k)
    ma20 = c.rolling(20).mean()
    out["dist_ma20"] = c / ma20 - 1
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    out["rsi14"] = 100 - 100 / (1 + gain / loss)
    out["vol20"] = out["ret1"].rolling(20).std()
    out["hl_range"] = (df.High - df.Low) / c
    out["target"] = (c.shift(-1) > c).astype(int)
    out["next_ret"] = out["ret1"].shift(-1)
    return out.dropna()


F = make_features(GOOG)
FEATS = ["ret_lag1", "ret_lag2", "ret_lag3", "ret_lag5", "ret_lag10",
         "dist_ma20", "rsi14", "vol20", "hl_range"]
n = len(F)
i1, i2 = int(n * .7), int(n * .85)
Xtr, Xva, Xte = F[FEATS].iloc[:i1], F[FEATS].iloc[i1:i2], F[FEATS].iloc[i2:]
ytr, yva, yte = F.target.iloc[:i1], F.target.iloc[i1:i2], F.target.iloc[i2:]


# ==================== CH5: classification ====================
def ch5():
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                  f1_score, confusion_matrix)
    from sklearn.preprocessing import StandardScaler
    import xgboost as xgb

    sc = StandardScaler().fit(Xtr)
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(max_depth=4, random_state=0),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=5, random_state=0),
        "XGBoost": xgb.XGBClassifier(n_estimators=150, max_depth=3, learning_rate=0.05,
                                      random_state=0, verbosity=0),
    }
    res = {}
    for name, m in models.items():
        Xa = sc.transform(Xtr) if "Logistic" in name else Xtr.values
        Xb = sc.transform(Xva) if "Logistic" in name else Xva.values
        m.fit(Xa, ytr)
        pred = m.predict(Xb)
        res[name] = {
            "acc": float(accuracy_score(yva, pred)),
            "prec": float(precision_score(yva, pred)),
            "rec": float(recall_score(yva, pred)),
            "f1": float(f1_score(yva, pred)),
        }
    RESULTS["ch5"] = res

    # fig 5.2: model comparison
    fig, ax = new_ax(price_axis=False, w=9.0, h=4.4)
    names = list(res)
    accs = [res[k]["acc"] * 100 for k in names]
    colors = [GREY, GOLD_LIGHT, GOLD, NAVY]
    bars = ax.bar(names, accs, color=colors, width=0.55, zorder=3)
    ax.axhline(50, color=RED, ls="--", lw=1.6)
    ax.text(0.1, 50.8, "خط الصدفة 50%", fontsize=9, color=RED, fontweight="bold")
    for b, a in zip(bars, accs):
        ax.text(b.get_x() + b.get_width() / 2, a + 0.4, f"{a:.1f}%", ha="center",
                fontsize=9.5, fontweight="bold", color=NAVY)
    ax.set_ylabel("الدقة على مجموعة التحقق %")
    ax.set_ylim(44, max(accs) + 4)
    ax.set_xlabel("أربع خوارزميات تصنيف على نفس مميزات GOOG الحقيقية (القسم 4.3)")
    save(fig, "fig-05-02")

    # fig 5.1: confusion matrix for best model
    best = max(res, key=lambda k: res[k]["acc"])
    m = models[best]
    Xb = sc.transform(Xva) if "Logistic" in best else Xva.values
    cm = confusion_matrix(yva, m.predict(Xb))
    fig, ax = plt.subplots(figsize=(6.4, 5.2), dpi=150)
    fig.patch.set_facecolor("white")
    im = ax.imshow(cm, cmap="Blues")
    labels = [["صحيح سلبي\n(توقع هبوط وهبط)", "خطأ إيجابي\n(توقع صعود وهبط)"],
              ["خطأ سلبي\n(توقع هبوط وصعد)", "صحيح إيجابي\n(توقع صعود وصعد)"]]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]}\n{labels[i][j]}", ha="center", va="center",
                    fontsize=9.5, color="white" if cm[i, j] > cm.max() * 0.6 else NAVY,
                    fontweight="bold")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["توقع: هبوط", "توقع: صعود"], fontsize=10)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["فعلي: هبوط", "فعلي: صعود"], fontsize=10)
    ax.set_title(f"مصفوفة الالتباس الحقيقية — {best} على تحقق GOOG", fontsize=10.5,
                 color=NAVY, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig-05-01")
    RESULTS["ch5"]["best"] = best


# ==================== CH6: regression ====================
def ch6():
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.svm import SVR
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    y_reg_tr, y_reg_va = F.next_ret.iloc[:i1], F.next_ret.iloc[i1:i2]
    sc = StandardScaler().fit(Xtr)
    Xa, Xb = sc.transform(Xtr), sc.transform(Xva)
    models = {
        "Linear": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Lasso": Lasso(alpha=1e-4),
        "SVR": SVR(kernel="rbf", C=1.0, epsilon=0.001),
    }
    res = {}
    preds = {}
    for name, m in models.items():
        m.fit(Xa, y_reg_tr)
        p = m.predict(Xb)
        preds[name] = p
        res[name] = {
            "rmse": float(np.sqrt(mean_squared_error(y_reg_va, p))),
            "mae": float(mean_absolute_error(y_reg_va, p)),
            "r2": float(r2_score(y_reg_va, p)),
        }
    RESULTS["ch6"] = res

    # fig 6.1: predicted vs actual next-day returns (Ridge), first 120 val days
    k = 120
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.4)
    ax.plot(y_reg_va.values[:k] * 100, color=GREY, lw=1.4, label="العائد الفعلي التالي")
    ax.plot(preds["Ridge"][:k] * 100, color=GOLD, lw=1.8, label="توقع Ridge")
    ax.set_ylabel("عائد اليوم التالي %")
    ax.set_xlabel("120 يوم تحقق حقيقيًا من GOOG — لاحظ ضآلة سعة التوقعات مقابل الواقع")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-06-01")


# ==================== CH7: unsupervised ====================
def ch7():
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    feats2 = F[["vol20", "dist_ma20"]].values
    sc = StandardScaler().fit(feats2)
    Z = sc.transform(feats2)
    km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Z)
    lab = km.labels_
    # order clusters by mean vol for stable naming
    order = np.argsort([F.vol20.values[lab == k].mean() for k in range(3)])
    names = {order[0]: ("هادئ", GREEN), order[1]: ("انتقالي", GOLD), order[2]: ("عاصف", RED)}
    RESULTS["ch7"] = {"cluster_share": {names[k][0]: float((lab == k).mean()) for k in range(3)}}

    close = GOOG.Close.reindex(F.index).values
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 6.2), dpi=150, sharex=True,
                                     gridspec_kw={"height_ratios": [2, 1]})
    fig.patch.set_facecolor("white")
    for k in range(3):
        nm, c = names[k]
        idx = np.where(lab == k)[0]
        ax1.scatter(idx, close[idx], s=4, color=c, label=f"نظام {nm}")
    ax1.legend(frameon=False, fontsize=9, loc="upper left")
    ax1.set_ylabel("سعر GOOG")
    ax1.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax1.spines[s].set_visible(False)
    ax2.plot(F.vol20.values * 100, color=NAVY, lw=1.0)
    ax2.set_ylabel("التقلب 20ي %")
    ax2.set_xlabel("تقسيم K-Means الفعلي لأيام GOOG إلى ثلاثة أنظمة سوق — أزمة 2008 كلها «عاصف»")
    ax2.grid(axis="y", color=GRID)
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    fig.tight_layout(pad=0.8)
    save(fig, "fig-07-01")

    # PCA on all features
    Zall = StandardScaler().fit_transform(F[FEATS])
    pca = PCA().fit(Zall)
    evr = pca.explained_variance_ratio_ * 100
    RESULTS["ch7"]["pca_first3"] = float(evr[:3].sum())
    fig, ax = new_ax(price_axis=False, w=8.6, h=4.2)
    ax.bar(range(1, len(evr) + 1), evr, color=NAVY, zorder=3)
    ax.plot(range(1, len(evr) + 1), np.cumsum(evr), color=GOLD, marker="o", lw=2,
            label="التراكمي")
    ax.set_xlabel("المكوّن الرئيسي (على مميزات GOOG التسع الحقيقية)")
    ax.set_ylabel("نسبة التباين المفسَّر %")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-07-02")

    # Isolation Forest anomalies on returns+range
    iso = IsolationForest(contamination=0.02, random_state=0)
    A = StandardScaler().fit_transform(F[["ret1", "hl_range"]])
    an = iso.fit_predict(A) == -1
    RESULTS["ch7"]["anomaly_days"] = int(an.sum())
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.2)
    ax.plot(close, color=GREY, lw=1.0)
    ax.scatter(np.where(an)[0], close[an], s=18, color=RED, zorder=5,
               label=f"أيام شاذة اكتشفها النموذج: {an.sum()}")
    ax.set_ylabel("سعر GOOG")
    ax.set_xlabel("Isolation Forest يكتشف الأيام غير الطبيعية آليًا — دون أن نعرّف له «الشذوذ»")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-07-03")


# ==================== CH8: XGBoost project on EURUSD ====================
def ch8():
    import xgboost as xgb
    from sklearn.metrics import accuracy_score

    E = make_features(EURUSD)
    ne = len(E)
    j1, j2 = int(ne * .7), int(ne * .85)
    Xtr_, Xva_, Xte_ = E[FEATS].iloc[:j1], E[FEATS].iloc[j1:j2], E[FEATS].iloc[j2:]
    ytr_, yva_, yte_ = E.target.iloc[:j1], E.target.iloc[j1:j2], E.target.iloc[j2:]

    # small hyperparameter search on validation
    grid = [(d, lr, ne_) for d in (2, 3, 4) for lr in (0.03, 0.07) for ne_ in (100, 200)]
    best, best_acc = None, 0
    for d, lr, nn in grid:
        m = xgb.XGBClassifier(max_depth=d, learning_rate=lr, n_estimators=nn,
                               random_state=0, verbosity=0).fit(Xtr_, ytr_)
        a = accuracy_score(yva_, m.predict(Xva_))
        if a > best_acc:
            best, best_acc = (d, lr, nn), a
    d, lr, nn = best
    model = xgb.XGBClassifier(max_depth=d, learning_rate=lr, n_estimators=nn,
                               random_state=0, verbosity=0).fit(
        pd.concat([Xtr_, Xva_]), pd.concat([ytr_, yva_]))
    test_acc = accuracy_score(yte_, model.predict(Xte_))
    RESULTS["ch8"] = {"best_params": {"max_depth": d, "lr": lr, "n_estimators": nn},
                      "val_acc": float(best_acc), "test_acc": float(test_acc)}

    # fig 8.1 feature importance (real)
    imp = model.feature_importances_
    order = np.argsort(imp)
    fig, ax = new_ax(price_axis=False, w=8.6, h=4.6)
    ax.barh([FEATS[i] for i in order], imp[order] * 100, color=NAVY, zorder=3)
    ax.set_xlabel("أهمية الميزة % في نموذج XGBoost المدرّب فعليًا على EURUSD")
    save(fig, "fig-08-01")

    # fig 8.2 strategy equity curve on TEST (long if predict up) vs buy&hold
    pred = model.predict(Xte_)
    next_ret = E.next_ret.iloc[j2:].values
    strat = np.where(pred == 1, next_ret, 0.0)
    cost = 0.00002  # spread تقريبي لكل تغيير مركز
    switches = np.abs(np.diff(pred, prepend=pred[0]))
    strat = strat - switches * cost
    eq_s = (1 + pd.Series(strat)).cumprod()
    eq_b = (1 + pd.Series(next_ret)).cumprod()
    RESULTS["ch8"]["strat_total"] = float(eq_s.iloc[-1] - 1)
    RESULTS["ch8"]["bh_total"] = float(eq_b.iloc[-1] - 1)
    fig, ax = new_ax(price_axis=False, w=9.2, h=4.4)
    ax.plot(eq_b.values, color=GREY, lw=1.6, label="شراء واحتفاظ")
    ax.plot(eq_s.values, color=GOLD, lw=1.8, label="استراتيجية النموذج (مع تكلفة تنفيذ)")
    ax.axhline(1.0, color=GRID)
    ax.set_ylabel("نمو وحدة رأس مال")
    ax.set_xlabel(f"مجموعة اختبار EURUSD غير المرئية ({len(pred)} ساعة تداول حقيقية)")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig-08-02")


for f in (ch5, ch6, ch7, ch8):
    f()
    print(f.__name__, "done")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics_part3.json"), "w") as fh:
    json.dump(RESULTS, fh, indent=1, ensure_ascii=False)
print(json.dumps(RESULTS, indent=1, ensure_ascii=False))
