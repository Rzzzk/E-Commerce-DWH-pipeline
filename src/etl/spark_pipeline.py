from pyspark.sql import SparkSession
from src.config.db_config import JDBC_URL, get_connection_properties

def create_spark_session():
    """Initializes and returns a Spark session with the Oracle JDBC driver."""
    print("Initializing Spark Session...")
    return SparkSession.builder \
        .appName("Ecommerce_DWH_ETL") \
        .config("spark.jars.packages", "com.oracle.database.jdbc:ojdbc8:21.9.0.0") \
        .getOrCreate()

def extract_and_enrich_data(spark):
    """Extracts tables from Oracle and joins them into an enriched DataFrame."""
    props = get_connection_properties()
    
    print("Extracting Data from Oracle...")
    fact_df = spark.read.jdbc(url=JDBC_URL, table="FACT_ORDER_LINE", properties=props)
    dim_date_df = spark.read.jdbc(url=JDBC_URL, table="DIM_DATE", properties=props)
    dim_category_df = spark.read.jdbc(url=JDBC_URL, table="DIM_CATEGORY", properties=props)

    print("Enriching Dataset with Dimensions...")
    enriched_df = fact_df.join(dim_date_df, "DATE_KEY", "left") \
                         .join(dim_category_df, "CATEGORY_KEY", "left")
                         
    return fact_df, enriched_df