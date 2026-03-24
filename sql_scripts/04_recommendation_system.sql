-- Replace '11' with the Product_ID you are testing
WITH TargetProduct AS (
    -- We use a Subquery here to ensure this CTE returns something 
    -- even if the product has zero sales
    SELECT 
        p.product_key, 
        NVL(MAX(f.category_key), 0) as category_key 
    FROM Dim_Product p
    LEFT JOIN Fact_Order_Line f ON p.product_key = f.product_key
    WHERE p.product_key = 11
    GROUP BY p.product_key
),
CrossSells AS (
    -- Finds products bought by the same customers
    SELECT f2.product_key, COUNT(*) as freq
    FROM Fact_Order_Line f1
    JOIN Fact_Order_Line f2 ON f1.customer_key = f2.customer_key
    WHERE f1.product_key = 11 AND f2.product_key != 11
    GROUP BY f2.product_key
),
ProductMetrics AS (
    -- Calculate General Business Indicators for ALL products
    SELECT 
        p.product_key,
        p.product_name,
        NVL(MAX(f.category_key), 0) as item_cat,
        AVG(f.profit_amount / NULLIF(f.net_amount, 0)) as avg_margin,
        SUM(f.quantity) as total_sold
    FROM Dim_Product p
    LEFT JOIN Fact_Order_Line f ON p.product_key = f.product_key
    GROUP BY p.product_key, p.product_name
)
SELECT 
    pm.product_name,
    -- Normalized Scoring Logic (Per Requirement 4)
    ROUND(
        (NVL(cs.freq, 0) * 15) +                                     -- Association Strength
        (CASE WHEN pm.item_cat = tp.category_key AND tp.category_key != 0 
              THEN 25 ELSE 0 END) +                                  -- Category Trend
        (NVL(pm.avg_margin, 0) * 40) +                               -- Profitability Stability
        (NVL(pm.total_sold, 0) * 0.2)                                -- Purchase Frequency
    , 2) as RECOMMENDATION_SCORE
FROM ProductMetrics pm
-- This LEFT JOIN is the FIX: it prevents the query from collapsing if tp is empty
LEFT JOIN TargetProduct tp ON 1=1 
LEFT JOIN CrossSells cs ON pm.product_key = cs.product_key
WHERE pm.product_key != NVL(tp.product_key, -1) -- Don't recommend the item itself
ORDER BY RECOMMENDATION_SCORE DESC
FETCH FIRST 4 ROWS ONLY;