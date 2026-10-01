# Cafeteria Orders: Auto-generated Results

Raw orders loaded: 5,961,005
- Unparseable date/amount rows removed: 0
- Duplicate order ids removed: 0
- Invalid branch ids removed: 1
- Partial last day (2025-04-01) excluded. Data range: 2024-04-01 to 2025-03-31

## Order status mix
paid_or_cancel
paid        5435472
cancel       400575
pending      107703
rejected        138
- Paid orders kept: 5,338,959 (dropped 96,199 zero-value and 314 orders above Rs 5,000 as outliers/test entries)

## Branch summary (paid orders)
            orders      revenue  avg_ticket  cancel_rate_%
branch_id                                                 
2          2178795  148352808.3        68.1            7.7
1          2095284  148003207.6        70.6            6.7
9           591111   39648815.8        67.1            7.1
4           442944   23894289.0        53.9            0.0
10           30448    1749113.0        57.4           18.0
3              377      33359.0        88.5            9.6

Peak hours (top 3): 17, 13, 16

Orders by weekday:
weekday
Monday       1007963
Tuesday      1107836
Wednesday    1092827
Thursday     1070638
Friday        907602
Saturday      111143
Sunday         40950

Payment modes:
mode_of_transaction
paytm       1694658
Upi         1058725
Cash         445245
Paytm        419720
cca          387011
QR           386030
razorpay     335722
Card         203708

Order channels:
order_through
mobile app    3056964
sok           1256271
pos           1025724

## Top 10 dishes by quantity
                                        qty     revenue
dish_name                                              
Ginger Tea                           690323  10511982.0
Regular Tea                          293910   4480809.0
Reboot Chai                          182819   2814630.0
Bombay Cutting Chai (Cutting Glass)  140179   2161860.0
Filter Kaapi                         137151   2502899.0
Veg Meal Combo                       113262   6274795.0
Irani Chai                           107004   2192166.0
Monday Morning Tea                    98423   1524025.0
Nescafe                               97223   1490049.0
Masala Dosa                           92491   4098450.0

## Top 5 dishes by revenue
                           qty     revenue
dish_name                                 
Ginger Tea              690323  10511982.0
Tandoor Veg Combo        69624   7315830.0
Veg Meal                 83284   6453501.0
Veg Meal Combo          113262   6274795.0
Indian Thali Veg Combo   90868   4624445.0

Note: order_details has 6,670,342 lines for paid orders (coverage is lower than the orders table).

## Forecast for branch 2
Days in series: 365, zero-order days: 0, mean orders/day: 5969

Backtest on last 14 days:
                                           MAE  MAPE_%
Seasonal naive (same weekday last week)  974.6    26.1
Holt-Winters additive                    842.6    23.2
Holt-Winters damped trend                850.9    23.4
Holt-Winters no trend                    842.9    22.8

Selected model: Holt-Winters additive

## 7-day forecast
      date   weekday  forecast_orders  lower_95  upper_95
2025-04-01   Tuesday             7667      4485     10849
2025-04-02 Wednesday             7587      4405     10769
2025-04-03  Thursday             7221      4039     10403
2025-04-04    Friday             5413      2231      8595
2025-04-05  Saturday                0         0      3182
2025-04-06    Sunday                0         0      3182
2025-04-07    Monday             6916      3734     10098

## Top counters by revenue, branch 2
counter_id
17.0    17520038.0
15.0    17057815.0
12.0    15849662.0
11.0    12865235.0
16.0    11812856.0
18.0    11175522.0
20.0    10058795.0
14.0     9351984.0
13.0     8430180.0
19.0     7745605.0