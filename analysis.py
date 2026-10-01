import pandas as pd, numpy as np, matplotlib, warnings
matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
OUT = "outputs/"
rep = []
def log(s=""):
    print(s); rep.append(str(s))
def save(name):
    plt.tight_layout(); plt.savefig(OUT + name, dpi=130); plt.close()

# ---------- 1. LOAD ----------
o = pd.read_csv("data/orders_clean.csv", low_memory=False)
log(f"# Cafeteria Orders: Auto-generated Results\n\nRaw orders loaded: {len(o):,}")

# ---------- 2. CLEAN ----------
o["order_date"] = pd.to_datetime(o["order_date"], errors="coerce")
for c in ["sub_total", "tax_amount", "discount_amount", "grand_total"]:
    o[c] = pd.to_numeric(o[c], errors="coerce")
bad = o["order_date"].isna().sum() + o["grand_total"].isna().sum()
o = o.dropna(subset=["order_date", "grand_total"])
dups = o.duplicated("id").sum(); o = o.drop_duplicates("id")
inv_branch = (o.branch_id <= 0).sum(); o = o[o.branch_id > 0]
last_day = o.order_date.dt.normalize().max()
o = o[o.order_date < last_day]          # last day is partial, drop it
log(f"- Unparseable date/amount rows removed: {bad:,}")
log(f"- Duplicate order ids removed: {dups:,}")
log(f"- Invalid branch ids removed: {inv_branch:,}")
log(f"- Partial last day ({last_day.date()}) excluded. Data range: {o.order_date.min().date()} to {(last_day - pd.Timedelta(days=1)).date()}")

# status mix and cancel rate per branch (before filtering to paid)
status = o.paid_or_cancel.value_counts()
log("\n## Order status mix\n" + status.to_string())
canc = (o.assign(c=o.paid_or_cancel.eq("cancel")).groupby("branch_id").c.mean() * 100).round(1)

# keep only completed (paid) orders with positive, non-extreme amounts
p = o[o.paid_or_cancel == "paid"]
zero = (p.grand_total <= 0).sum(); p = p[p.grand_total > 0]
big = (p.grand_total > 5000).sum(); p = p[p.grand_total <= 5000]
log(f"- Paid orders kept: {len(p):,} (dropped {zero:,} zero-value and {big:,} orders above Rs 5,000 as outliers/test entries)")
p = p.copy()
p["date"] = p.order_date.dt.normalize()
p["hour"] = p.order_date.dt.hour
p["weekday"] = p.order_date.dt.day_name()
p["month"] = p.order_date.dt.to_period("M").astype(str)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ---------- 3. EDA ----------
br = p.groupby("branch_id").agg(orders=("id", "count"), revenue=("grand_total", "sum"),
                                avg_ticket=("grand_total", "mean")).round(1)
br["cancel_rate_%"] = canc
br = br.sort_values("orders", ascending=False)
br.to_csv(OUT + "branch_summary.csv")
log("\n## Branch summary (paid orders)\n" + br.to_string())

ax = br.revenue.plot.bar(figsize=(7, 4), title="Revenue by branch (Rs)"); ax.set_xlabel("branch_id"); save("01_revenue_by_branch.png")

hr = p.groupby("hour").size()
hr.plot.bar(figsize=(10, 4), title="Orders by hour of day"); save("02_orders_by_hour.png")
log(f"\nPeak hours (top 3): {', '.join(str(h) for h in hr.sort_values(ascending=False).index[:3])}")

wd = p.groupby("weekday").size().reindex(days)
wd.plot.bar(figsize=(8, 4), title="Orders by weekday"); save("03_orders_by_weekday.png")
log("\nOrders by weekday:\n" + wd.to_string())

top4 = br.index[:4]
mt = p[p.branch_id.isin(top4)].groupby(["month", "branch_id"]).size().unstack()
mt.plot(marker="o", figsize=(11, 4), title="Monthly orders by branch"); save("04_monthly_trend.png")

pm = p.mode_of_transaction.value_counts().head(8)
pm.plot.barh(figsize=(7, 4), title="Payment mode"); save("05_payment_mode.png")
log("\nPayment modes:\n" + pm.to_string())

ch = p.order_through.value_counts()
ch.plot.pie(autopct="%1.0f%%", figsize=(5, 5), title="Order channel", ylabel=""); save("06_order_channel.png")
log("\nOrder channels:\n" + ch.to_string())

# ---------- 4. DISHES AND COUNTERS ----------
d = pd.read_csv("data/order_details_clean.csv", low_memory=False)
d["order_quantity"] = pd.to_numeric(d.order_quantity, errors="coerce")
d["dish_cal_price"] = pd.to_numeric(d.dish_cal_price, errors="coerce")
d = d[d.order_id.isin(p.id)]
d["dish_name"] = d.dish_name.astype(str).str.strip().str.title()
dish = d.groupby("dish_name").agg(qty=("order_quantity", "sum"), revenue=("dish_cal_price", "sum")).sort_values("qty", ascending=False)
dish.head(25).to_csv(OUT + "top_dishes.csv")
dish.head(10).qty.sort_values().plot.barh(figsize=(8, 5), title="Top 10 dishes by quantity"); save("07_top_dishes.png")
log("\n## Top 10 dishes by quantity\n" + dish.head(10).round(0).to_string())
log("\n## Top 5 dishes by revenue\n" + dish.sort_values("revenue", ascending=False).head(5).round(0).to_string())
log(f"\nNote: order_details has {len(d):,} lines for paid orders (coverage is lower than the orders table).")

# ---------- 5. FORECAST: next 7 days, busiest branch ----------
B = br.index[0]
pb = p[p.branch_id == B]
daily = pb.groupby("date").size()
daily = daily.reindex(pd.date_range(daily.index.min(), daily.index.max()), fill_value=0).asfreq("D")
log(f"\n## Forecast for branch {B}\nDays in series: {len(daily)}, zero-order days: {(daily == 0).sum()}, mean orders/day: {daily.mean():.0f}")

H = 14
train, test = daily[:-H], daily[-H:]
def mape(a, f):
    m = a > 0
    return float((abs(a[m] - f[m]) / a[m]).mean() * 100)
cands = {}
cands["Seasonal naive (same weekday last week)"] = pd.Series(daily[-H - 7:-7].values[:H], index=test.index)
for name, kw in [("Holt-Winters additive", dict(trend="add")), ("Holt-Winters damped trend", dict(trend="add", damped_trend=True)),
                 ("Holt-Winters no trend", dict(trend=None))]:
    m = ExponentialSmoothing(train, seasonal="add", seasonal_periods=7, **kw).fit()
    cands[name] = pd.Series(m.forecast(H).values, index=test.index)
res = pd.DataFrame({k: {"MAE": (test - v).abs().mean(), "MAPE_%": mape(test, v)} for k, v in cands.items()}).T.round(1)
log("\nBacktest on last 14 days:\n" + res.to_string())
best = res["MAE"].idxmin(); log(f"\nSelected model: {best}")

resid_sd = float((test - cands[best]).std())
if best.startswith("Seasonal"):
    fc = pd.Series(daily[-7:].values, index=pd.date_range(daily.index[-1] + pd.Timedelta(days=1), periods=7))
else:
    kw = {"Holt-Winters additive": dict(trend="add"), "Holt-Winters damped trend": dict(trend="add", damped_trend=True),
          "Holt-Winters no trend": dict(trend=None)}[best]
    fm = ExponentialSmoothing(daily, seasonal="add", seasonal_periods=7, **kw).fit()
    fc = pd.Series(fm.forecast(7).values, index=pd.date_range(daily.index[-1] + pd.Timedelta(days=1), periods=7))
fc = fc.clip(lower=0).round()
out = pd.DataFrame({"date": fc.index.date, "weekday": fc.index.day_name(), "forecast_orders": fc.astype(int).values,
                    "lower_95": (fc - 1.96 * resid_sd).clip(lower=0).round().astype(int).values,
                    "upper_95": (fc + 1.96 * resid_sd).round().astype(int).values})
out.to_csv(OUT + "forecast_next_7_days.csv", index=False)
log("\n## 7-day forecast\n" + out.to_string(index=False))

plt.figure(figsize=(11, 4))
daily[-60:].plot(label="Actual")
cands[best].plot(label="Backtest prediction", linestyle=":") if not best.startswith("Seasonal") or True else None
fc.plot(marker="o", label="Forecast")
plt.fill_between(fc.index, out.lower_95, out.upper_95, alpha=0.2)
plt.legend(); plt.title(f"7-day order forecast, branch {B} ({best})"); save("08_forecast.png")

# weekday x hour heatmap for the forecast branch
hm = pb.groupby(["weekday", "hour"]).size().unstack(fill_value=0).reindex(days)
plt.figure(figsize=(12, 4)); sns.heatmap(hm, cmap="YlOrRd"); plt.title(f"Branch {B}: orders by weekday and hour"); save("09_heatmap.png")

# counters for the selected branch
d["branch_id"] = d.order_id.map(p.set_index("id").branch_id)
ct = d[d.branch_id == B].groupby("counter_id").dish_cal_price.sum().sort_values(ascending=False).head(10)
log(f"\n## Top counters by revenue, branch {B}\n" + ct.round(0).to_string())

open(OUT + "REPORT_auto.md", "w", encoding="utf8").write("\n".join(rep))
print("\nDONE. See the outputs folder.")
