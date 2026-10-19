"""Step 2: forecast BYD Seagull adoption (global), t = 1 is 2023.

Scenario A: p and q from Tesla, M from the Fermi estimate.
Scenario B: q from Tesla, M from Fermi, p set so 2023 matches actual sales.
Scenario C (main): q from Tesla, p and M fitted to the actual 2023-2025 sales.
Then: check against Jan-Sep 2026 sales and a sensitivity test on q.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import bass_model as bm

FIRST_YEAR, N = 2023, 8                      # forecast 2023-2030
sales = pd.read_csv("data/seagull_sales.csv")
y = sales.loc[sales["year"].isin(["2023", "2024", "2025"]), "units"].to_numpy() / 1e6
ytd_2026 = sales.loc[sales["year"] == "2026 Jan-Sep", "units"].iloc[0] / 1e6

tesla = pd.read_csv("data/tesla_parameters.csv").set_index("method").loc["NLS"]
p_t, q_t = tesla["p"], tesla["q"]

fi = pd.read_csv("data/fermi_inputs.csv").set_index("input")["value"]
M_fermi = (fi["Global electric car sales in 2024"]
           * fi["Share of EV sales in the small low-cost city car segment"]
           * fi["Seagull share of that segment"]
           * fi["Years the Seagull nameplate stays on sale"]) / 1e6
print(f"Fermi M = {M_fermi:.2f} million cars")

p_B = bm.p_matching_first_period(y[0], M_fermi, q_t)
(M_C, p_C), (seM_C, sep_C) = bm.fit_p_and_M(y, q_t)
print(f"Scenario C fit: M = {M_C:.2f} (se {seM_C:.2f}), p = {p_C:.4f} (se {sep_C:.4f})")

scen = {"A_lookalike": (M_fermi, p_t), "B_fermi_calibrated": (M_fermi, p_B),
        "C_fitted_main": (M_C, p_C)}
k = np.arange(1, N + 1)
years = np.arange(FIRST_YEAR, FIRST_YEAR + N)
fc = pd.DataFrame({"year": years, "t": k})
fc["actual_mln"] = list(y) + [np.nan] * (N - len(y))
rows = []
for name, (M, p) in scen.items():
    a = bm.per_period(k, M, p, q_t)
    fc[f"{name}_new_mln"] = a
    fc[f"{name}_cum_mln"] = a.cumsum()
    rows.append({"scenario": name, "M_mln": M, "p": p, "q": q_t,
                 "t_peak": bm.t_peak(p, q_t), "peak_year": int(years[np.argmax(a)]),
                 "peak_units_mln": a.max(),
                 "error_2024_pct": 100 * (a[1] - y[1]) / y[1],
                 "error_2025_pct": 100 * (a[2] - y[2]) / y[2]})
fc.round(4).to_csv("data/seagull_forecast.csv", index=False)
summ = pd.DataFrame(rows)
summ.to_csv("data/seagull_scenarios.csv", index=False)
print(summ.round(4).to_string(index=False))
print(fc.round(3).to_string(index=False))

# check against 2026 so far (9 of 12 months, treated as 75% of the year)
check = pd.DataFrame([{
    "scenario": n,
    "model_2026_full_year_mln": fc.loc[3, f"{n}_new_mln"],
    "model_2026_jan_sep_mln": 0.75 * fc.loc[3, f"{n}_new_mln"],
    "actual_2026_jan_sep_mln": ytd_2026,
} for n in scen])
check.to_csv("data/seagull_check_2026.csv", index=False)
print(check.round(3).to_string(index=False))

# sensitivity: what if Seagull's imitation effect is weaker or stronger than Tesla's?
sens = []
for q_s in [0.8 * q_t, q_t, 1.2 * q_t]:
    (M_s, p_s), _ = bm.fit_p_and_M(y, q_s)
    a = bm.per_period(k, M_s, p_s, q_s)
    sens.append({"q": q_s, "M_mln": M_s, "p": p_s, "units_2026_mln": a[3],
                 "cum_2030_mln": a.sum(), "peak_year": int(years[np.argmax(a)])})
sens = pd.DataFrame(sens)
sens.to_csv("data/seagull_sensitivity.csv", index=False)
print(sens.round(3).to_string(index=False))

# charts
green, light, grey = "#1b7f5c", "#bfe3d3", "#9a9a9a"
fig, ax = plt.subplots(figsize=(8, 4.2))
w = 0.27
ax.bar(years - w, fc["C_fitted_main_new_mln"], w, color=green, label="C: fitted to Seagull data (main)")
ax.bar(years, fc["B_fermi_calibrated_new_mln"], w, color=light, label="B: Fermi M, p matched to 2023")
ax.bar(years + w, fc["A_lookalike_new_mln"], w, color=grey, label="A: pure Tesla look-alike")
ax.scatter(years[:3], y, color="black", zorder=5, label="Actual sales 2023-2025")
ax.scatter([2026], [ytd_2026 / 0.75], marker="x", s=60, color="black", zorder=5,
           label="2026 pace (Jan-Sep scaled to a year)")
ax.set_title("BYD Seagull: predicted cars sold per year")
ax.set_ylabel("Million cars")
ax.set_xticks(years)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig("img/seagull_new_adopters.png", dpi=160)

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(years, fc["C_fitted_main_cum_mln"], "o-", color=green, label=f"C (main), M = {M_C:.2f}M")
ax.plot(years, fc["B_fermi_calibrated_cum_mln"], "s--", color="#4fa784", label=f"B, M = {M_fermi:.2f}M")
ax.plot(years, fc["A_lookalike_cum_mln"], "^:", color=grey, label="A: pure look-alike")
ax.plot(years[:3], np.cumsum(y), "k*", ms=10, label="Actual cumulative")
ax.set_title("BYD Seagull: predicted cumulative adopters")
ax.set_ylabel("Million cars")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout()
fig.savefig("img/seagull_cumulative.png", dpi=160)
