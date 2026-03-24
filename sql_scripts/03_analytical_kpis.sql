
--1. Revenue & 2. Gross Profit
--Explanation: Revenue is the total money brought in, and Gross Profit is what remains after subtracting the cost of the goods sold.
--Simplified: Revenue = Sum of net_amount, Gross Profit = Sum of profit_amount

SELECT 
    d.full_date,
    SUM(f.net_amount) AS daily_revenue,
    SUM(SUM(f.net_amount)) OVER (ORDER BY d.full_date) AS running_total_revenue,
    SUM(f.profit_amount) AS daily_profit,
    SUM(SUM(f.profit_amount)) OVER (ORDER BY d.full_date) AS running_total_profit
FROM Fact_Order_Line f
JOIN Dim_Date d ON f.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;


--3. Average Order Value (AOV)
--Explanation: How much money, on average, a customer spends every time they make a purchase.
--Simplified: Total Revenue ÷ Total Number of Unique Orders.

WITH OrderBaskets AS (
    -- Grouping line items into a single "Order" per customer, per day
    SELECT 
        customer_key,
        date_key,
        SUM(net_amount) AS order_revenue
    FROM Fact_Order_Line
    GROUP BY customer_key, date_key
)
SELECT 
    customer_key,
    date_key,
    order_revenue,
    ROUND(AVG(order_revenue) OVER (), 2) AS historical_aov,
    -- Label orders as above or below average
    CASE 
        WHEN order_revenue > AVG(order_revenue) OVER () THEN 'Above Average'
        ELSE 'Below Average' 
    END AS aov_performance
FROM OrderBaskets
ORDER BY date_key;


--4. Customer Lifetime Value (CLV)
--Explanation: The total amount of money a specific customer has spent with your business from their very first purchase to their most recent.
--Simplified: The running sum of a single customer's purchases.

SELECT 
    c.customer_id,
    d.full_date,
    f.net_amount AS transaction_amount,
    SUM(f.net_amount) OVER (
        PARTITION BY c.customer_key 
        ORDER BY d.full_date
    ) AS current_lifetime_value
FROM Fact_Order_Line f
JOIN Dim_Customer c ON f.customer_key = c.customer_key
JOIN Dim_Date d ON f.date_key = d.date_key
ORDER BY c.customer_id, d.full_date;

--5. Repeat Purchase Rate
--Explanation: What percentage of your customers come back to buy a second, third, or fourth time?
--Simplified: (Count of customers with > 1 order) ÷ (Total count of unique customers).

WITH CustomerOrders AS (
    SELECT 
        customer_key,
        date_key,
        -- Ranks distinct dates per customer to find the sequence of their orders
        DENSE_RANK() OVER (PARTITION BY customer_key ORDER BY date_key) AS purchase_sequence
    FROM Fact_Order_Line
),
MaxSequencePerCustomer AS (
    SELECT 
        customer_key,
        MAX(purchase_sequence) AS total_lifetime_orders
    FROM CustomerOrders
    GROUP BY customer_key
)
SELECT 
    COUNT(customer_key) AS total_customers,
    SUM(CASE WHEN total_lifetime_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        SUM(CASE WHEN total_lifetime_orders > 1 THEN 1 ELSE 0 END) / COUNT(customer_key) * 100
    , 2) AS repeat_purchase_rate_pct
FROM MaxSequencePerCustomer;


-- 6. Profit Margin
-- Explanation: For every dollar of revenue generated, how much is actual profit?
-- Simplified: (Total Profit ÷ Total Revenue) * 100.

WITH CategoryFinancials AS (
    SELECT 
        c.category_name,
        SUM(f.net_amount) AS total_revenue,
        SUM(f.profit_amount) AS total_profit
    FROM Fact_Order_Line f
    JOIN Dim_Category c ON f.category_key = c.category_key
    GROUP BY c.category_name
)
SELECT 
    category_name,
    total_revenue,
    total_profit,
    ROUND((total_profit / total_revenue) * 100, 2) AS profit_margin_pct,
    -- Rank the categories by their margin
    RANK() OVER (ORDER BY (total_profit / total_revenue) DESC) AS margin_rank
FROM CategoryFinancials;


--7. Revenue Growth Rate (Month-over-Month)
--Explanation: The speed at which your revenue is increasing (or decreasing) compared to the previous month.
--Simplified: ((This Month's Revenue - Last Month's Revenue) ÷ Last Month's Revenue) * 100.

WITH MonthlyRevenue AS (
    SELECT 
        d.year,
        d.month,
        d.month_name,
        SUM(f.net_amount) AS current_month_revenue
    FROM Fact_Order_Line f
    JOIN Dim_Date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month, d.month_name
)
SELECT 
    year,
    month_name,
    current_month_revenue,
    -- Retrieve the revenue from the previous chronological row
    LAG(current_month_revenue, 1) OVER (ORDER BY year, month) AS prev_month_revenue,
    
    -- Calculate the growth percentage
    ROUND(
        (current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY year, month)) 
        / NULLIF(LAG(current_month_revenue, 1) OVER (ORDER BY year, month), 0) * 100
    , 2) AS mom_growth_rate_pct
FROM MonthlyRevenue
ORDER BY year, month;


--------------------------------
-- Time-Based & Ranking Analysis
--------------------------------

-- 1. Cumulative Revenue & 4. Moving Average (3-day window)
SELECT 
    full_date,
    DAILY_REVENUE,
    SUM(DAILY_REVENUE) OVER (ORDER BY full_date) as CUMULATIVE_REVENUE,
    AVG(DAILY_REVENUE) OVER (ORDER BY full_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as MOVING_AVG_3DAY
FROM (SELECT d.full_date, SUM(f.net_amount) as DAILY_REVENUE 
      FROM Fact_Order_Line f JOIN Dim_Date d ON f.date_key = d.date_key GROUP BY d.full_date);

-- 7. Rank products within each category & 8. Contribution %
SELECT 
    category_name,
    product_name,
    total_revenue,
    RANK() OVER (PARTITION BY category_name ORDER BY total_revenue DESC) as PRODUCT_RANK,
    ROUND(100 * total_revenue / SUM(total_revenue) OVER (PARTITION BY category_name), 2) as CONTRIBUTION_PCT
FROM (
    SELECT c.category_name, p.product_name, SUM(f.net_amount) as total_revenue
    FROM Fact_Order_Line f 
    JOIN Dim_Product p ON f.product_key = p.product_key
    JOIN Dim_Category c ON f.category_key = c.category_key
    GROUP BY c.category_name, p.product_name
);




--------------------------------
-- Customer Behavior & Segmentation
--------------------------------


-- 13. Time intervals between purchases
SELECT 
    customer_key,
    full_date,
    LAG(full_date) OVER (PARTITION BY customer_key ORDER BY full_date) as PREVIOUS_PURCHASE_DATE,
    full_date - LAG(full_date) OVER (PARTITION BY customer_key ORDER BY full_date) as DAYS_SINCE_LAST_PURCHASE
FROM (SELECT DISTINCT customer_key, d.full_date 
      FROM Fact_Order_Line f JOIN Dim_Date d ON f.date_key = d.date_key);

-- 15. Segment customers into Quartiles (Spending Tiers)
SELECT 
    customer_key,
    total_spent,
    NTILE(4) OVER (ORDER BY total_spent DESC) as SPENDING_QUARTILE -- 1 is Top Tier
FROM (SELECT customer_key, SUM(net_amount) as total_spent FROM Fact_Order_Line GROUP BY customer_key);