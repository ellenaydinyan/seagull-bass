# Bass Model Homework – BYD Seagull

DS 223 Marketing Analytics (AUA) · Elen Aydinyan

**Innovation (TIME Best Inventions 2025, Transportation):** BYD Seagull
<https://time.com/collections/best-inventions-2025/7318540/byd-seagull/>

**Look-alike:** Tesla, using its yearly deliveries from 2012 to 2025 (Tesla's quarterly delivery reports).

The report is in `report/`, as an editable Word file (`report.docx`) and a PDF (`report.pdf`).

## Results

| | p | q | M |
|---|---|---|---|
| Tesla (look-alike, NLS, R² = 0.997) | 0.00028 | 0.625 | 11.9M cars |
| BYD Seagull, main scenario C (global) | 0.088 (fitted to 2023–2025 sales) | 0.625 (from Tesla) | 2.7M cars (fitted; Fermi estimate was 4.3M) |

In the main scenario, Seagull sales peaked in 2025 at about 0.54M cars, and the total reaches about 2.6M by 2030. Real sales for January–September 2026 are falling even faster than the model predicts.

## Files

```
├── README.md
├── requirements.txt
├── bass_model.py              # Bass functions: F(t), adopters per period, NLS, OLS, fit with q fixed, peak time
├── step1_tesla_fit.py         # estimates p, q, M for Tesla and draws the Tesla charts
├── step2_seagull_forecast.py  # Fermi M, Seagull scenarios A/B/C, 2026 check, sensitivity to q, charts
├── data/
│   ├── tesla_deliveries.csv        # input: Tesla deliveries per year with source
│   ├── seagull_sales.csv           # input: Seagull sales 2023, 2024, 2025, Jan–Sep 2026
│   ├── fermi_inputs.csv            # input: numbers and assumptions for the Fermi estimate
│   ├── tesla_parameters.csv        # output: p, q, M for Tesla (NLS and OLS)
│   ├── tesla_fitted.csv            # output: actual vs fitted Tesla deliveries
│   ├── seagull_forecast.csv        # output: Seagull sales per year 2023–2030, all scenarios
│   ├── seagull_scenarios.csv       # output: parameters, peak and errors for each scenario
│   ├── seagull_check_2026.csv      # output: model vs real Jan–Sep 2026 sales
│   └── seagull_sensitivity.csv     # output: results with q 20% lower / higher
├── img/
│   ├── tesla_fit.png               # Tesla deliveries and Bass fits
│   ├── tesla_cumulative.png        # Tesla cumulative deliveries, actual vs model
│   ├── seagull_new_adopters.png    # Seagull predicted sales per year
│   └── seagull_cumulative.png      # Seagull predicted cumulative sales
├── report/
│   ├── report_source.md            # report text (Markdown)
│   ├── report.docx                 # report (Word)
│   ├── report.pdf                  # report (PDF)
│   └── format_word.py              # formats the Word file (fonts, tables, images)
└── references/
    └── references.md               # all references with links
```

## How to run

```bash
pip install -r requirements.txt
python step1_tesla_fit.py
python step2_seagull_forecast.py
```

Run step 1 before step 2, because step 2 uses Tesla's parameters from `data/tesla_parameters.csv`.

To rebuild the Word report:

```bash
cd report
pandoc report_source.md -o report.docx --resource-path=.:..
python format_word.py report.docx
```
