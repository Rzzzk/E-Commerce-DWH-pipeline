import os
import pandas as pd
from pyspark.sql.window import Window
import pyspark.sql.functions as F

# Import our custom ETL functions
from src.etl.spark_pipeline import create_spark_session, extract_and_enrich_data

def generate_kpi_marts():
    # ==========================================
    # 1. Initialize & Extract Data
    # ==========================================
    spark = create_spark_session()
    
    # Unpack the dictionary of raw tables and the master joined table
    dataframes, enriched_df = extract_and_enrich_data(spark)
    fact_df = dataframes["FACT_ORDER_LINE"]
    
    print("Calculating Business KPIs...")

    # ==========================================
    # 2. Overall Dashboard KPIs (Scalars)
    # ==========================================
    
    # KPI 1 & 2: Total Revenue & Gross Profit
    # Logic: Sum of all Net Amounts and Profit Amounts across the entire fact table.
    totals = fact_df.agg(
        F.sum("NET_AMOUNT").alias("TOTAL_REVENUE"),
        F.sum("PROFIT_AMOUNT").alias("TOTAL_PROFIT")
    ).collect()[0]

    total_rev = totals["TOTAL_REVENUE"] or 0
    total_prof = totals["TOTAL_PROFIT"] or 0

    # KPI 6: Profit Margin (%)
    # Logic: (Gross Profit / Total Revenue) * 100
    margin_pct = round((total_prof / total_rev) * 100, 2) if total_rev > 0 else 0

    # KPI 3: Average Order Value (AOV)
    # Logic: Group by Customer and Date to simulate an "Order Basket", sum the revenue per basket, then average it.
    order_baskets = fact_df.groupBy("CUSTOMER_KEY", "DATE_KEY").agg(F.sum("NET_AMOUNT").alias("BASKET_REVENUE"))
    aov_row = order_baskets.select(F.avg("BASKET_REVENUE")).collect()[0][0]
    aov = round(aov_row, 2) if aov_row else 0

    # KPI 5: Repeat Purchase Rate (%)
    # Logic: Count customers who have purchased on more than one distinct day vs total unique customers.
    customer_activity = fact_df.groupBy("CUSTOMER_KEY").agg(F.countDistinct("DATE_KEY").alias("PURCHASE_DAYS"))
    total_customers = customer_activity.count()
    repeat_customers = customer_activity.filter(F.col("PURCHASE_DAYS") > 1).count()
    repeat_rate = round((repeat_customers / total_customers) * 100, 2) if total_customers > 0 else 0

    # Save overall KPIs into a single-row DataFrame for the dashboard cards
    overall_kpis_pdf = pd.DataFrame([{
        "Total_Revenue": total_rev, 
        "Gross_Profit": total_prof,
        "Profit_Margin_Pct": margin_pct, 
        "AOV": aov, 
        "Repeat_Purchase_Rate_Pct": repeat_rate
    }])

    # ==========================================
    # 3. Dimensional Data Marts (For Charts & Tables)
    # ==========================================

    # KPI 4: Customer Lifetime Value (CLV)
    # Logic: Total historical revenue generated per individual customer.
    clv_df = fact_df.groupBy("CUSTOMER_KEY").agg(
        F.round(F.sum("NET_AMOUNT"), 2).alias("CLV"),
        F.countDistinct("DATE_KEY").alias("TOTAL_ORDERS")
    ).orderBy(F.desc("CLV"))

    # KPI 7: Revenue Growth Rate (Month-over-Month)
    # Logic: Use Window functions to get the previous month's revenue, then calculate the % difference.
    monthly_rev = enriched_df.groupBy("YEAR", "MONTH", "MONTH_NAME").agg(
        F.sum("NET_AMOUNT").alias("CURR_REV")
    )
    window_spec = Window.orderBy("YEAR", "MONTH")
    growth_df = monthly_rev.withColumn("PREV_REV", F.lag("CURR_REV", 1).over(window_spec)) \
        .withColumn("MOM_GROWTH_PCT", F.round(((F.col("CURR_REV") - F.col("PREV_REV")) / F.col("PREV_REV")) * 100, 2)) \
        .orderBy("YEAR", "MONTH")

    # Daily Trend Data Mart (For Line Charts)
    daily_kpi_df = enriched_df.groupBy("FULL_DATE").agg(
        F.round(F.sum("NET_AMOUNT"), 2).alias("DAILY_REVENUE")
    ).orderBy("FULL_DATE")

    # Category Performance Data Mart (For Bar Charts & Filtering)
    category_kpi_df = enriched_df.groupBy("CATEGORY_NAME").agg(
        F.round(F.sum("NET_AMOUNT"), 2).alias("TOTAL_REVENUE"),
        F.round(F.sum("PROFIT_AMOUNT"), 2).alias("TOTAL_PROFIT")
    ).withColumn("PROFIT_MARGIN_PCT", F.round((F.col("TOTAL_PROFIT") / F.col("TOTAL_REVENUE")) * 100, 2))

    # ==========================================
    # 4. Export Data Marts to CSV
    # ==========================================
    print("Exporting Data Marts to CSV...")
    
    # Resolve the correct output directory (ecommerce_dwh_project/data)
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
    os.makedirs(output_dir, exist_ok=True)

    # Convert PySpark DataFrames to Pandas and save
    overall_kpis_pdf.to_csv(f"{output_dir}/overall_kpis.csv", index=False)
    daily_kpi_df.toPandas().to_csv(f"{output_dir}/daily_kpis.csv", index=False)
    category_kpi_df.toPandas().to_csv(f"{output_dir}/category_kpis.csv", index=False)
    clv_df.toPandas().to_csv(f"{output_dir}/customer_clv.csv", index=False)
    growth_df.toPandas().to_csv(f"{output_dir}/monthly_growth.csv", index=False)

    print("Pipeline Execution Complete!")

if __name__ == "__main__":
    generate_kpi_marts()