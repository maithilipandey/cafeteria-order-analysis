-- Orders by weekday (0 = Sunday)
SELECT strftime('%w', order_date) AS weekday, COUNT(*) AS orders
FROM orders WHERE paid_or_cancel='paid' AND grand_total>0
GROUP BY weekday ORDER BY weekday;

-- Orders by channel
SELECT order_through, COUNT(*) AS orders
FROM orders WHERE paid_or_cancel='paid' AND grand_total>0
GROUP BY order_through ORDER BY orders DESC;

-- Payment modes
SELECT mode_of_transaction, COUNT(*) AS orders
FROM orders WHERE paid_or_cancel='paid' AND grand_total>0
GROUP BY mode_of_transaction ORDER BY orders DESC;
