# Cafeteria Order Data: Analysis and 7-Day Forecast

## Executive Summary

This project analyzes approximately **5.96 million cafeteria order records** from FY 2024–25 across multiple branches and counters. The analysis focuses on data extraction and cleaning, exploratory data analysis, branch and operational patterns, customer ordering behavior, and a simple **7-day demand forecast** for a selected branch.

The project was completed as part of the **Kanishka Software Pvt Ltd internship challenge: Cafeteria Order Data – Quick Analysis & Forecast Challenge**.

### Key Findings

- **Branch 1 and Branch 2** account for approximately **80% of analyzed paid orders**.
- Demand varies significantly by **branch, weekday, and hour of day**.
- A relatively small group of menu items contributes a substantial share of order volume and revenue.
- **Mobile ordering** is the largest ordering channel, accounting for approximately **57%** of orders.
- **Branch 10** has a notably high cancellation rate of approximately **18%**, which should be investigated.
- Average ticket value varies considerably across branches.
- A **7-day forecast** was generated for Branch 2 using Holt-Winters exponential smoothing and evaluated against a seasonal-naive baseline.

> **Note:** These are descriptive observations from the available dataset. Some operational interpretations and data-quality issues require validation against the original business system.

---

## 1. Approach

### Data Source

The source data was provided as a large SQL dump of approximately **11 GB**.

Because importing the complete dump into MySQL was impractical within the 24-hour challenge window, the project uses a streaming extraction approach.

### Data Pipeline

```text
11 GB SQL Dump
      │
      ▼
Streaming Extraction
      │
      ▼
Relevant Order + Order Detail CSVs
      │
      ▼
Cleaning & Validation
      │
      ▼
Exploratory Data Analysis
      │
      ├── Branch Analysis
      ├── Time Analysis
      ├── Payment Analysis
      ├── Channel Analysis
      └── Menu Analysis
      │
      ▼
Branch 2 Daily Demand Series
      │
      ▼
Forecast Model Comparison
      │
      ▼
7-Day Forecast + Business Insights
```

### Main Scripts

- `extract_csv.py` — streams the SQL dump and extracts the required columns into CSV files.
- `analysis.py` — performs cleaning, EDA, aggregation, visualization, model evaluation, and forecasting.

The extraction process produced approximately:

- **5.96 million order records**
- **7.43 million order-detail records**

The large CSV files are intentionally **not included in the repository** because of their size.

### Analysis Period

The primary analysis covers:

**2024-04-01 to 2025-03-31**

A partial **2025-04-01** record was present in the source data but was excluded from the analysis because the day was incomplete.

---

## 2. Data Cleaning & Validation

The following cleaning and validation steps were applied:

- Parsed order dates and timestamps.
- Parsed order amounts into numeric values.
- Checked for unparseable dates and amounts.
- Checked for duplicate order IDs.
- Removed one invalid branch ID (`-1`).
- Excluded the incomplete **2025-04-01** record from the main analysis.
- Treated only **paid orders** as completed sales.
- Excluded cancelled, pending, and rejected orders from sales metrics while retaining status information for cancellation analysis.
- Identified **96,199 zero-value orders** and **314 orders above ₹5,000** as likely test/outlier records and removed them from the final paid-order analysis.
- The raw maximum order value was approximately **₹996,000**, making the outlier filtering necessary for meaningful business-level analysis.

### Final Dataset

After cleaning and filtering:

**5,338,959 paid orders** remained for the main analysis.

The approximately **5.44 million paid orders** refers to the paid-order population before the final zero-value and outlier exclusions.

---

## 3. Key Insights

### 3.1 Branch Performance

| Branch | Orders | Revenue (₹) | Avg. Ticket (₹) | Cancellation Rate |
|---|---:|---:|---:|---:|
| Branch 2 | 2,178,795 | 148,352,808.3 | 68.1 | 7.7% |
| Branch 1 | 2,095,284 | 148,003,207.6 | 70.6 | 6.7% |
| Branch 9 | 591,111 | 39,648,815.8 | 67.1 | 7.1% |
| Branch 4 | 442,944 | 23,894,289.0 | 53.9 | 0.0% |
| Branch 10 | 30,448 | 1,749,113.0 | 57.4 | 18.0% |
| Branch 3 | 377 | 33,359.0 | 88.5 | 9.6% |

Branch 1 and Branch 2 together account for approximately **80% of the analyzed paid-order volume**.

Branch 2 is the largest branch by both **order count and revenue**.

Branch 10 has an unusually high cancellation rate of approximately **18%** and should be investigated further.

Branch 4 shows a **0% recorded cancellation rate**. This may indicate missing or unrecorded cancellation data and should be validated against the source-system definitions.

Branch 3 has only **377 orders**, so its average ticket and cancellation rate should not be overinterpreted because of the very small sample size.

![Revenue by Branch](01_revenue_by_branch.png)

---

### 3.2 Weekly Demand Pattern

Order volume is heavily concentrated on weekdays:

- Monday–Thursday: approximately **1.0–1.1 million orders per day of the week**
- Friday: approximately **0.91 million**
- Saturday: approximately **0.11 million**
- Sunday: approximately **0.04 million**

The strong weekday/weekend difference is consistent with an **office or campus-style cafeteria**, although this cannot be confirmed from the dataset alone.

![Orders by Weekday](03_orders_by_weekday.png)

---

### 3.3 Hourly Demand

The busiest observed hours include:

- **17:00**
- **13:00**
- **16:00**

This suggests that staffing, inventory, and counter capacity should be planned around these recurring demand peaks.

![Orders by Hour](02_orders_by_hour.png)

---

### 3.4 Monthly Trend

Monthly order and revenue trends were analyzed to identify changes in demand throughout the year.

![Monthly Trend](04_monthly_trend.png)

---

### 3.5 Ordering Channels

Approximate order-channel distribution:

- **Mobile App:** 57%
- **Kiosk:** 24%
- **POS:** 19%

The high mobile share indicates that digital ordering is an important part of the cafeteria ordering workflow.

![Order Channel](06_order_channel.png)

---

### 3.6 Payment Methods

Payments are predominantly digital, with **Paytm accounting for approximately 40%** of transactions, followed by UPI and cash.

The source data contains capitalization inconsistencies such as `paytm` and `Paytm`. These should be standardized in a production data pipeline before reporting or aggregation.

![Payment Mode](05_payment_mode.png)

---

### 3.7 Top Menu Items

**Ginger Tea** is the highest-volume item, with approximately:

- **690,000 units**
- **₹10.5 million in revenue**

The top items are dominated by tea and coffee products, while combination/meal items contribute significantly to overall revenue.

![Top Dishes](07_top_dishes.png)

---

## 4. Forecasting

### Selected Branch

The forecast was generated for **Branch 2**, the busiest branch in the dataset.

The model uses daily paid-order counts over approximately **365 days**, with an average daily volume of around **5,969 orders**.

### Forecasting Approach

The following models were compared using a **14-day holdout period**:

1. Seasonal Naive baseline
2. Holt-Winters with additive trend and weekly seasonality
3. Holt-Winters with damped trend and weekly seasonality
4. Holt-Winters with no trend and weekly seasonality

### Model Comparison

| Model | MAE | MAPE |
|---|---:|---:|
| Seasonal Naive | 974.6 | 26.1% |
| Holt-Winters Additive | **842.6** | 23.2% |
| Holt-Winters Damped Trend | 850.9 | 23.4% |
| Holt-Winters No Trend | 842.9 | **22.8%** |

The **Holt-Winters additive model** was selected based on the **lowest MAE**, while the no-trend variant produced a slightly lower MAPE.

MAE was used as the primary selection criterion because it provides an absolute measure of forecast error in the same unit as the target variable: daily orders.

### 7-Day Forecast for Branch 2

| Date | Day | Forecast | Lower Bound | Upper Bound |
|---|---|---:|---:|---:|
| 2025-04-01 | Tue | 7,667 | 4,485 | 10,849 |
| 2025-04-02 | Wed | 7,587 | 4,405 | 10,769 |
| 2025-04-03 | Thu | 7,221 | 4,039 | 10,403 |
| 2025-04-04 | Fri | 5,413 | 2,231 | 8,595 |
| 2025-04-05 | Sat | ~0 | 0 | 3,182 |
| 2025-04-06 | Sun | ~0 | 0 | 3,182 |
| 2025-04-07 | Mon | 6,916 | 3,734 | 10,098 |

The forecast reflects the strong weekday/weekend pattern observed in the historical data.

The lower and upper values are **approximate uncertainty bounds based on backtest residual variability**, rather than formal statistical prediction intervals.

![7-Day Forecast](08_forecast.png)

---

## 5. Forecast Limitations

The forecasting approach is intentionally simple and suitable for a 24-hour analysis challenge.

Important limitations include:

- The Holt-Winters model achieves an MAPE of approximately **23%**, so the forecast should be treated as directional rather than highly precise.
- The validation period contains only **14 days**, which limits the robustness of model evaluation.
- No holiday calendar was incorporated.
- Only approximately one year of data is available, so annual seasonality cannot be reliably learned.
- Weekend demand is very low and forecast values were clipped at zero, which can simplify the representation of small non-zero weekend demand.
- Branch IDs are used directly because the branch-name mapping was not incorporated into the analysis.
- Timestamps were used as recorded; no timezone conversion was applied.

---

## 6. Business Insights & Recommendations

### 1. Plan staffing around demand peaks

The strongest hourly demand occurs around **13:00 and 16:00–17:00**.

Staffing and counter capacity can therefore be aligned with these recurring peaks.

The hourly and branch/weekday heatmaps can be used to support more detailed shift planning.

### 2. Align weekend operations with observed demand

Weekend order volume is substantially lower than weekday volume.

Staffing and inventory levels can therefore be adjusted to the observed demand pattern, while the business can separately investigate whether the low weekend volume is operationally expected.

### 3. Prioritize high-volume beverages

Tea and coffee products, particularly Ginger Tea, contribute significant order volume.

Maintaining sufficient stock of high-volume beverages can help avoid stockouts during peak periods.

### 4. Investigate Branch 10 cancellations

Branch 10 has an approximately **18% cancellation rate**, substantially higher than the major branches.

The business should investigate whether this is caused by operational issues, payment failures, order handling, or differences in cancellation recording.

### 5. Standardize payment labels

Payment-method labels such as `paytm` and `Paytm` should be standardized before production reporting.

This will prevent the same payment method from being split into multiple categories during aggregation.

### 6. Improve forecasting with additional business information

A future forecasting system could incorporate:

- Holiday calendars
- Special events
- Weather information
- Branch-specific models
- Day-of-week effects
- Promotions
- Historical cancellation patterns
- Longer validation periods
- More advanced forecasting models

---

## 7. Business Summary

| Metric | Result |
|---|---|
| Raw order records | ~5.96 million |
| Final paid orders analyzed | 5,338,959 |
| Order-detail records | ~7.43 million |
| Branches analyzed | 6 |
| Largest branch by orders | Branch 2 |
| Largest branch by revenue | Branch 2 |
| Highest recorded cancellation rate | Branch 10 — 18.0% |
| Highest-volume menu item | Ginger Tea |
| Largest ordering channel | Mobile App — ~57% |
| Forecast branch | Branch 2 |
| Forecast horizon | 7 days |
| Primary forecasting approach | Holt-Winters |
| Primary validation metric | MAE |

---

## 8. Repository Structure

```text
cafeteria-order-analysis/
│
├── extract_csv.py
├── analysis.py
├── queries.sql
├── requirements.txt
├── README.md
│
├── outputs/
│   ├── 01_revenue_by_branch.png
│   ├── 02_orders_by_hour.png
│   ├── 03_orders_by_weekday.png
│   ├── 04_monthly_trend.png
│   ├── 05_payment_mode.png
│   ├── 06_order_channel.png
│   ├── 07_top_dishes.png
│   ├── 08_forecast.png
│   ├── 09_heatmap.png
│   ├── branch_summary.csv
│   ├── forecast_next_7_days.csv
│   ├── top_dishes.csv
│   └── REPORT_auto.md
│
└── data/
    └── Generated CSV files
```

> The large raw SQL dump and extracted CSV datasets are not included in the repository because of their size.

---

## 9. How to Run

### 1. Clone the repository

```bash
git clone https://github.com/maithilipandey/cafeteria-order-analysis.git
cd cafeteria-order-analysis
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the SQL dump path

Open `extract_csv.py` and update the SQL dump path:

```python
BIG = r"C:\path\to\Cafeteria Order Data.sql"
```

### 4. Extract the required data

```bash
python extract_csv.py
```

The script streams the large SQL dump and writes the required order and order-detail data to CSV files.

### 5. Run the analysis

```bash
python analysis.py
```

This generates the analysis tables, charts, forecast, and report outputs.

---

## 10. SQL Analysis

The repository also contains:

```text
queries.sql
```

This file contains SQL equivalents for the major analysis queries.

The queries were written for **SQLite-style analysis** and were not required for the primary execution pipeline because the original dataset was provided as a large SQL dump and the Python streaming approach was used for the challenge.

---

## 11. Output Files

### Analysis Tables

- `branch_summary.csv`
- `top_dishes.csv`
- `forecast_next_7_days.csv`

### Visualizations

### Revenue by branch
![Revenue by branch](outputs/01_revenue_by_branch.png)

### Orders by hour of day
![Orders by hour](outputs/02_orders_by_hour.png)

### Orders by weekday
![Orders by weekday](outputs/03_orders_by_weekday.png)

### Monthly orders by branch
![Monthly trend](outputs/04_monthly_trend.png)

### Payment modes
![Payment mode](outputs/05_payment_mode.png)

### Order channel
![Order channel](outputs/06_order_channel.png)

### Top 10 dishes
![Top dishes](outputs/07_top_dishes.png)

### 7-day forecast (Branch 2)
![Forecast](outputs/08_forecast.png)

### Weekday x hour heatmap (Branch 2)
![Heatmap](outputs/09_heatmap.png)

---

## 12. Technologies Used

- **Python**
- **Pandas**
- **NumPy**
- **Matplotlib**
- **Seaborn**
- **Statsmodels**
- **CSV / SQL data processing**
- **Holt-Winters Exponential Smoothing**

---

## 13. Conclusion

This project demonstrates an end-to-end workflow for working with a large transactional dataset under a limited analysis window:

**large-scale data extraction → cleaning → validation → exploratory analysis → business insights → forecasting → model evaluation**

The analysis highlights strong weekday demand patterns, branch-level differences, digital ordering adoption, high-volume menu categories, and potential operational issues such as unusually high cancellation rates.

The forecasting component provides a simple baseline for short-term demand planning while also identifying the limitations that would need to be addressed before deploying a production forecasting system.

---

### Internship Challenge

**Cafeteria Order Data – Quick Analysis & Forecast Challenge**

Prepared as part of the **Kanishka Software Pvt Ltd Internship Challenge**.

**Tools:** Python · Pandas · Statsmodels · Matplotlib · Seaborn

## Charts

### Revenue by branch
![Revenue by branch](outputs/01_revenue_by_branch.png)

### Orders by hour of day
![Orders by hour](outputs/02_orders_by_hour.png)

### Orders by weekday
![Orders by weekday](outputs/03_orders_by_weekday.png)

### Monthly orders by branch
![Monthly trend](outputs/04_monthly_trend.png)

### Payment modes
![Payment mode](outputs/05_payment_mode.png)

### Order channel
![Order channel](outputs/06_order_channel.png)

### Top 10 dishes
![Top dishes](outputs/07_top_dishes.png)

### 7-day forecast (Branch 2)
![Forecast](outputs/08_forecast.png)

### Weekday x hour heatmap (Branch 2)
![Heatmap](outputs/09_heatmap.png)
