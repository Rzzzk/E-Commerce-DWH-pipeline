-- 1. Generate 90 Days of Dates (Jan 1 to Mar 31, 2024)
INSERT INTO Dim_Date (date_key, full_date, day, month, month_name, quarter, year, week_number)
SELECT 
    TO_NUMBER(TO_CHAR(curr_date, 'YYYYMMDD')), curr_date,
    CAST(TO_CHAR(curr_date, 'DD') AS NUMBER), CAST(TO_CHAR(curr_date, 'MM') AS NUMBER),
    TO_CHAR(curr_date, 'Month'), TO_NUMBER(TO_CHAR(curr_date, 'Q')),
    CAST(TO_CHAR(curr_date, 'YYYY') AS NUMBER), TO_NUMBER(TO_CHAR(curr_date, 'WW'))
FROM (SELECT TO_DATE('2024-01-01', 'YYYY-MM-DD') + LEVEL - 1 AS curr_date FROM DUAL CONNECT BY LEVEL <= 90);

-- 2. Insert Categories (Keys 1 to 5)
INSERT INTO Dim_Category (category_name, parent_category, seasonal_flag) VALUES ('Laptops', 'Computers', 'N');
INSERT INTO Dim_Category (category_name, parent_category, seasonal_flag) VALUES ('Smartphones', 'Mobile', 'N');
INSERT INTO Dim_Category (category_name, parent_category, seasonal_flag) VALUES ('Televisions', 'Entertainment', 'Y');
INSERT INTO Dim_Category (category_name, parent_category, seasonal_flag) VALUES ('Audio', 'Entertainment', 'N');
INSERT INTO Dim_Category (category_name, parent_category, seasonal_flag) VALUES ('Accessories', 'Computers', 'N');

-- 3. Insert Products (Keys 1 to 10)
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('LAP-01', 'MacBook Pro M3', 'Apple', 'Ultrabook', DATE '2023-10-01');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('LAP-02', 'Dell XPS 15', 'Dell', 'Performance', DATE '2023-05-15');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('PHO-01', 'iPhone 15 Pro', 'Apple', 'Smartphone', DATE '2023-09-15');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('PHO-02', 'Galaxy S24 Ultra', 'Samsung', 'Smartphone', DATE '2024-01-20');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('TV-01', 'LG OLED C3 65"', 'LG', 'OLED TV', DATE '2023-04-10');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('TV-02', 'Samsung QLED 75"', 'Samsung', 'QLED TV', DATE '2023-03-20');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('AUD-01', 'Sony WH-1000XM5', 'Sony', 'Headphones', DATE '2022-05-12');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('AUD-02', 'AirPods Pro 2', 'Apple', 'Earbuds', DATE '2022-09-23');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('ACC-01', 'Logitech MX Master 3', 'Logitech', 'Mouse', DATE '2022-05-24');
INSERT INTO Dim_Product (product_id, product_name, brand, subcategory, launch_date) VALUES ('ACC-02', 'Anker 100W Charger', 'Anker', 'Power', DATE '2023-01-10');

-- 4. Insert Customers (Keys 1 to 5)
INSERT INTO Dim_Customer (customer_id, gender, age_group, city, region, registration_date, customer_segment) VALUES ('CUST-01', 'Male', '25-34', 'Cairo', 'Cairo Gov', DATE '2023-01-15', 'Premium');
INSERT INTO Dim_Customer (customer_id, gender, age_group, city, region, registration_date, customer_segment) VALUES ('CUST-02', 'Female', '18-24', 'Alexandria', 'Alex Gov', DATE '2023-06-20', 'Standard');
INSERT INTO Dim_Customer (customer_id, gender, age_group, city, region, registration_date, customer_segment) VALUES ('CUST-03', 'Male', '35-44', 'Giza', 'Giza Gov', DATE '2022-11-05', 'VIP');
INSERT INTO Dim_Customer (customer_id, gender, age_group, city, region, registration_date, customer_segment) VALUES ('CUST-04', 'Female', '25-34', 'Mansoura', 'Dakahlia', DATE '2023-08-12', 'Standard');
INSERT INTO Dim_Customer (customer_id, gender, age_group, city, region, registration_date, customer_segment) VALUES ('CUST-05', 'Male', '45-54', 'Cairo', 'Cairo Gov', DATE '2021-03-10', 'Premium');

-- 5. Insert Payment & Shipping (Keys 1 to 4 & 1 to 3)
INSERT INTO Dim_Payment (payment_method) VALUES ('Credit Card');
INSERT INTO Dim_Payment (payment_method) VALUES ('Debit Card');
INSERT INTO Dim_Payment (payment_method) VALUES ('PayPal');
INSERT INTO Dim_Payment (payment_method) VALUES ('Cash on Delivery');

INSERT INTO Dim_Shipping (shipping_type, delivery_days) VALUES ('Standard', 5);
INSERT INTO Dim_Shipping (shipping_type, delivery_days) VALUES ('Express', 2);
INSERT INTO Dim_Shipping (shipping_type, delivery_days) VALUES ('Same Day', 0);


DECLARE
    v_date_key NUMBER;
    v_prod_key NUMBER;
    v_cat_key NUMBER;
    v_qty NUMBER;
    v_price NUMBER;
    v_gross NUMBER;
    v_disc NUMBER;
    v_net NUMBER;
    v_cost NUMBER;
BEGIN
    FOR i IN 1..100 LOOP
        -- 1. Pick a random date in Q1 2024
        v_date_key := TO_NUMBER(TO_CHAR(DATE '2024-01-01' + TRUNC(DBMS_RANDOM.VALUE(0, 90)), 'YYYYMMDD'));
        
        -- 2. Pick a random product (1-10)
        v_prod_key := TRUNC(DBMS_RANDOM.VALUE(1, 11)); 
        
        -- 3. Match the product to its correct Category & assign a Base Price
        IF v_prod_key IN (1, 2) THEN 
            v_cat_key := 1; v_price := 1500;   -- Laptops
        ELSIF v_prod_key IN (3, 4) THEN 
            v_cat_key := 2; v_price := 1000;   -- Phones
        ELSIF v_prod_key IN (5, 6) THEN 
            v_cat_key := 3; v_price := 1200;   -- TVs
        ELSIF v_prod_key IN (7, 8) THEN 
            v_cat_key := 4; v_price := 250;    -- Audio
        ELSE 
            v_cat_key := 5; v_price := 100;    -- Accessories
        END IF;
        
        -- 4. Calculate Financials (Qty: 1-3, Discount: 0-10%, Margin: ~40%)
        v_qty := TRUNC(DBMS_RANDOM.VALUE(1, 4));
        v_gross := v_price * v_qty;
        v_disc := ROUND(v_gross * DBMS_RANDOM.VALUE(0, 0.10), 2);
        v_net := v_gross - v_disc;
        v_cost := ROUND(v_gross * 0.6, 2); 
        
        -- 5. Insert Row
        INSERT INTO Fact_Order_Line (
            date_key, customer_key, product_key, category_key, payment_key, shipping_key,
            quantity, gross_amount, discount_amount, net_amount, cost_amount, profit_amount
        ) VALUES (
            v_date_key, 
            TRUNC(DBMS_RANDOM.VALUE(1, 6)), -- Random Customer 1-5
            v_prod_key, 
            v_cat_key, 
            TRUNC(DBMS_RANDOM.VALUE(1, 5)), -- Random Payment 1-4
            TRUNC(DBMS_RANDOM.VALUE(1, 4)), -- Random Shipping 1-3
            v_qty, v_gross, v_disc, v_net, v_cost, (v_net - v_cost)
        );
    END LOOP;
    COMMIT;
END;
/

COMMIT;


-- Save the transactions
COMMIT;

SELECT * FROM FACT_ORDER_LINE;
SELECT * FROM DIM_DATE;
SELECT * FROM DIM_CUSTOMER;
SELECT * FROM DIM_PRODUCT;
SELECT * FROM DIM_CATEGORY;
SELECT * FROM DIM_PAYMENT;
SELECT * FROM DIM_SHIPPING;


TRUNCATE TABLE FACT_ORDER_LINE;
TRUNCATE TABLE DIM_DATE;
TRUNCATE TABLE DIM_CUSTOMER;
TRUNCATE TABLE DIM_PRODUCT;
TRUNCATE TABLE DIM_CATEGORY;
TRUNCATE TABLE DIM_PAYMENT;
TRUNCATE TABLE DIM_SHIPPING;


DROP TABLE Fact_Order_Line;
DROP TABLE Dim_Shipping;
DROP TABLE Dim_Payment;
DROP TABLE Dim_Product;
DROP TABLE Dim_Category;
DROP TABLE Dim_Customer;
DROP TABLE Dim_Date;