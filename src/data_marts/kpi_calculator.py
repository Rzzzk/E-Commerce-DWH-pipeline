import os
import pandas as pd
from pyspark.sql.window import Window
import pyspark.sql.functions as F

# Import our custom ETL functions
from src.etl.spark_pipeline import create_spark_session, extract_and_enrich_data

def generate_kpi_marts():
    # 1. Get Data from ETL Layer
    spark = create_spark_session()
    fact_df, enriched_df = extract_and_enrich_data(spark)
    
    print("Calculating Business KPIs...")

    # ==========================================
    # A. Overall Scalar KPIs
    # ==========================================
    totals = fact_df.agg(
        F.sum("NET_AMOUNT").alias("TOTAL_REVENUE"),
        F.sum("PROFIT_AMOUNT").alias("TOTAL_PROFIT")
    ).collect()[0]

    total_rev = totals["TOTAL_REVENUE"] or 0
    total_prof = totals["TOTAL_PROFIT"] or 0
    margin_pct = round((total_prof / total_rev) * 100, 2) if total_rev > 0 else 0

    order_baskets = fact_df.groupBy("CUSTOMER_KEY", "DATE_KEY").agg(F.sum("NET_AMOUNT").alias("ORDER_REVENUE"))
    aov = round(order_baskets.select(F.avg("ORDER_REVENUE")).collect()[0][0], 2)

    cust_counts = fact_df.groupBy("CUSTOMER_KEY").agg(F.countDistinct("DATE_KEY").alias("DAYS"))
    total_cust = cust_counts.count()
    repeat_cust = cust_counts.filter(F.col("DAYS") > 1).count()
    repeat_rate = round((repeat_cust / total_cust) * 100, 2) if total_cust > 0 else 0

    overall_kpis_pdf = pd.DataFrame([{
        "Total_Revenue": total_rev, "Gross_Profit": total_prof,
        "Profit_Margin_Pct": margin_pct, "AOV": aov, "Repeat_Purchase_Rate_Pct": repeat_rate
    }])

    # ==========================================
    # B. Daily & Category Data Marts
    # ==========================================
    daily_kpi_df = enriched_df.groupBy("FULL_DATE").agg(
        F.round(F.sum("NET_AMOUNT"), 2).alias("DAILY_REVENUE")
    ).orderBy("FULL_DATE")

    category_kpi_df = enriched_df.groupBy("CATEGORY_NAME").agg(
        F.round(F.sum("NET_AMOUNT"), 2).alias("TOTAL_REVENUE"),
        F.round(F.sum("PROFIT_AMOUNT"), 2).alias("TOTAL_PROFIT")
    ).withColumn("PROFIT_MARGIN_PCT", F.round((F.col("TOTAL_PROFIT") / F.col("TOTAL_REVENUE")) * 100, 2))

    # ==========================================
    # C. CLV & MoM Growth Data Marts
    # ==========================================
    clv_df = fact_df.groupBy("CUSTOMER_KEY").agg(
        F.round(F.sum("NET_AMOUNT"), 2).alias("CLV"),
        F.countDistinct("DATE_KEY").alias("TOTAL_ORDERS")
    ).orderBy(F.desc("CLV"))

    monthly_rev = enriched_df.groupBy("YEAR", "MONTH", "MONTH_NAME").agg(F.sum("NET_AMOUNT").alias("CURR_REV"))
    window_spec = Window.orderBy("YEAR", "MONTH")
    growth_df = monthly_rev.withColumn("PREV_REV", F.lag("CURR_REV", 1).over(window_spec)) \
        .withColumn("MOM_GROWTH_PCT", F.round(((F.col("CURR_REV") - F.col("PREV_REV")) / F.col("PREV_REV")) * 100, 2)) \
        .orderBy("YEAR", "MONTH")

    # ==========================================
    # Exporting
    # ==========================================
    print("Exporting Data Marts to CSV...")
    # Navigate up from src/data_marts to the root 'data' folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
    os.makedirs(output_dir, exist_ok=True)

    overall_kpis_pdf.to_csv(f"{output_dir}/overall_kpis.csv", index=False)
    daily_kpi_df.toPandas().to_csv(f"{output_dir}/daily_kpis.csv", index=False)
    category_kpi_df.toPandas().to_csv(f"{output_dir}/category_kpis.csv", index=False)
    clv_df.toPandas().to_csv(f"{output_dir}/customer_clv.csv", index=False)
    growth_df.toPandas().to_csv(f"{output_dir}/monthly_growth.csv", index=False)

    print("Pipeline Execution Complete!")

if __name__ == "__main__":
    generate_kpi_marts()