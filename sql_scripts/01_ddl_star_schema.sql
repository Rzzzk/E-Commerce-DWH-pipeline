-- ==========================================
-- 1. DIMENSION TABLES
-- ==========================================

-- Dim_Date
CREATE TABLE Dim_Date (
    date_key NUMBER PRIMARY KEY,
    full_date DATE NOT NULL,
    day NUMBER(2),
    month NUMBER(2),
    month_name VARCHAR2(20),
    quarter NUMBER(1),
    year NUMBER(4),
    week_number NUMBER(2)
);

-- Dim_Customer
CREATE TABLE Dim_Customer (
    customer_key NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id VARCHAR2(50) NOT NULL,
    gender VARCHAR2(10),
    age_group VARCHAR2(20),
    city VARCHAR2(100),
    region VARCHAR2(100),
    registration_date DATE,
    customer_segment VARCHAR2(50)
);

-- Dim_Product
CREATE TABLE Dim_Product (
    product_key NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id VARCHAR2(50) NOT NULL,
    product_name VARCHAR2(255),
    brand VARCHAR2(100),
    subcategory VARCHAR2(100),
    launch_date DATE
);

-- Dim_Category
CREATE TABLE Dim_Category (
    category_key NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR2(100) NOT NULL,
    parent_category VARCHAR2(100),
    seasonal_flag CHAR(1)
);

-- Dim_Payment
CREATE TABLE Dim_Payment (
    payment_key NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_method VARCHAR2(50) NOT NULL
);

-- Dim_Shipping
CREATE TABLE Dim_Shipping (
    shipping_key NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    shipping_type VARCHAR2(50) NOT NULL,
    delivery_days NUMBER(3)
);

-- ==========================================
-- 2. FACT TABLE
-- ==========================================

-- Fact_Order_Line
CREATE TABLE Fact_Order_Line (
    order_line_key NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    date_key NUMBER NOT NULL,
    customer_key NUMBER NOT NULL,
    product_key NUMBER NOT NULL,
    category_key NUMBER NOT NULL,
    payment_key NUMBER NOT NULL,
    shipping_key NUMBER NOT NULL,
    
    quantity NUMBER(10) NOT NULL,
    gross_amount NUMBER(15, 2),
    discount_amount NUMBER(15, 2),
    net_amount NUMBER(15, 2),
    cost_amount NUMBER(15, 2),
    profit_amount NUMBER(15, 2),
    
    CONSTRAINT fk_fact_date FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key),
    CONSTRAINT fk_fact_customer FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
    CONSTRAINT fk_fact_product FOREIGN KEY (product_key) REFERENCES Dim_Product(product_key),
    CONSTRAINT fk_fact_category FOREIGN KEY (category_key) REFERENCES Dim_Category(category_key),
    CONSTRAINT fk_fact_payment FOREIGN KEY (payment_key) REFERENCES Dim_Payment(payment_key),
    CONSTRAINT fk_fact_shipping FOREIGN KEY (shipping_key) REFERENCES Dim_Shipping(shipping_key)
);