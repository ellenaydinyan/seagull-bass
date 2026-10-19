"""Step 1: estimate p, q, M for the look-alike (Tesla deliveries 2012-2025)."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import bass_model as bm

df = pd.read_csv("data/tesla_deliveries.csv")
y = df["deliveries"].to_numpy() / 1e6          # million cars
k = np.arange(1, len(y) + 1)                   # t = 1 is 2012

(M, p, q), (seM, sep, seq) = bm.fit_nls(y, start=(15, 0.001, 0.4))
M_o, p_o, q_o = bm.fit_ols(y)

df["fitted_nls_mln"] = bm.per_period(k, M, p, q)
df["fitted_ols_mln"] = bm.per_period(k, M_o, p_o, q_o)
df["cum_actual_mln"] = np.cumsum(y)
df["cum_fitted_nls_mln"] = M * bm.F(k, p, q)
df.round(4).to_csv("data/tesla_fitted.csv", index=False)

res = pd.DataFrame({
    "method": ["NLS", "OLS (Bass 1969)"],
    "p": [p, p_o], "q": [q, q_o], "M_mln": [M, M_o],
    "se_p": [sep, np.nan], "se_q": [seq, np.nan], "se_M": [seM, np.nan],
    "t_peak": [bm.t_peak(p, q), bm.t_peak(p_o, q_o)],
    "R2": [bm.r_squared(y, df["fitted_nls_mln"]), bm.r_squared(y, df["fitted_ols_mln"])],
})
res.to_csv("data/tesla_parameters.csv", index=False)
print(res.round(5).to_string(index=False))

green, grey = "#1b7f5c", "#7a7a7a"
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(df["year"], y, color="#bfe3d3", label="Actual deliveries")
ax.plot(df["year"], df["fitted_nls_mln"], "o-", color=green, lw=2, label="Bass fit (NLS)")
ax.plot(df["year"], df["fitted_ols_mln"], "x--", color=grey, label="Bass fit (OLS)")
ax.set_title("Tesla deliveries per year and the Bass model fit")
ax.set_ylabel("Million cars")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("img/tesla_fit.png", dpi=160)

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(df["year"], df["cum_actual_mln"], "o-", color="#222222", label="Actual cumulative")
ax.plot(df["year"], df["cum_fitted_nls_mln"], "--", color=green, label="Bass cumulative (NLS)")
ax.axhline(M, color=grey, ls=":", lw=1)
ax.text(2012, M + 0.2, f"M = {M:.1f}M", color=grey)
ax.set_title("Tesla cumulative deliveries")
ax.set_ylabel("Million cars")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="center left")
fig.tight_layout()
fig.savefig("img/tesla_cumulative.png", dpi=160)
