

WITH TargetProduct AS (
    -- 1. Identify the anchor product and its category
    SELECT 
        p.product_key, 
        NVL(MAX(f.category_key), 0) as category_key 
    FROM Dim_Product p
    LEFT JOIN Fact_Order_Line f ON p.product_key = f.product_key
    WHERE p.product_key = 11  ----------------------------------------------- set the Product_ID you are testing

    GROUP BY p.product_key
),
CrossSells AS (
    -- 2. Find "Market Basket" associations (Optimized)
    SELECT 
        f2.product_key, 
        COUNT(*) as freq,
        MAX(f2.date_key) as last_bought_together -- Identifies recency of the association
    FROM Fact_Order_Line f1
    JOIN Fact_Order_Line f2 ON f1.customer_key = f2.customer_key
    WHERE f1.product_key = 11 
      AND f2.product_key != 11
      -- Performance constraint: Only look at associations from the last 12 months
      -- AND f1.date_key >= TO_NUMBER(TO_CHAR(ADD_MONTHS(SYSDATE, -12), 'YYYYMMDD')) 
    GROUP BY f2.product_key
),
ProductMetrics AS (
    -- 3. Calculate Global Health Indicators for all products
    SELECT 
        p.product_key,
        p.product_name,
        NVL(MAX(f.category_key), 0) as item_cat,
        -- Cap margin at 1.0 (100%) to prevent data anomalies from breaking the score
        LEAST(NVL(AVG(f.profit_amount / NULLIF(f.net_amount, 0)), 0), 1) as avg_margin,
        NVL(SUM(f.quantity), 0) as total_sold,
        NVL(MAX(f.date_key), 0) as last_sold_date
    FROM Dim_Product p
    LEFT JOIN Fact_Order_Line f ON p.product_key = f.product_key
    GROUP BY p.product_key, p.product_name
)
-- 4. The Final Scoring Algorithm
SELECT 
    pm.product_name,
    ROUND(
        -- A. Association Strength (Heavy Weight)
        (NVL(cs.freq, 0) * 15) +                                     
        
        -- B. Category Fit (Medium Weight)
        (CASE WHEN pm.item_cat = tp.category_key AND tp.category_key != 0 THEN 25 ELSE 0 END) + 
        
        -- C. Profitability Stability (Percentage scaled by 40)
        (pm.avg_margin * 40) +                               
        
        -- D. Purchase Frequency / Popularity (Light Weight)
        -- Using LOG or a small multiplier prevents massive sellers from dominating
        (pm.total_sold * 0.2) +
        
        -- E. Recency of Demand (Bonus points if sold recently)
        (CASE WHEN pm.last_sold_date >= 20240201 THEN 10 ELSE 0 END)
        
    , 2) as RECOMMENDATION_SCORE
FROM ProductMetrics pm
LEFT JOIN TargetProduct tp ON 1=1 
LEFT JOIN CrossSells cs ON pm.product_key = cs.product_key
WHERE pm.product_key != NVL(tp.product_key, -1) 
ORDER BY RECOMMENDATION_SCORE DESC
FETCH FIRST 4 ROWS ONLY;