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
    """
    Dynamically extracts all Star Schema tables from Oracle, 
    stores them in a dictionary, and creates a fully enriched master DataFrame.
    """
    props = get_connection_properties()
    
    # 1. Define all tables in the Star Schema
    tables = [
        "FACT_ORDER_LINE", 
        "DIM_DATE", 
        "DIM_CUSTOMER", 
        "DIM_PRODUCT", 
        "DIM_CATEGORY", 
        "DIM_PAYMENT", 
        "DIM_SHIPPING"
    ]
    
    # 2. Extract data into a dictionary of DataFrames
    dataframes = {}
    print("Extracting Data from Oracle...")
    for table in tables:
        print(f" -> Reading table: {table}")
        dataframes[table] = spark.read.jdbc(url=JDBC_URL, table=table, properties=props)

    # 3. Create a fully denormalized "Enriched" DataFrame
    # We use the dictionary keys to grab the DataFrames and join them to the Fact table
    print("Enriching Dataset with all Dimensions...")
    enriched_df = dataframes["FACT_ORDER_LINE"] \
        .join(dataframes["DIM_DATE"], "DATE_KEY", "left") \
        .join(dataframes["DIM_CUSTOMER"], "CUSTOMER_KEY", "left") \
        .join(dataframes["DIM_PRODUCT"], "PRODUCT_KEY", "left") \
        .join(dataframes["DIM_CATEGORY"], "CATEGORY_KEY", "left") \
        .join(dataframes["DIM_PAYMENT"], "PAYMENT_KEY", "left") \
        .join(dataframes["DIM_SHIPPING"], "SHIPPING_KEY", "left")
                         
    # Return both the dictionary of raw tables (for specific aggregations) 
    # and the fully enriched table (for broad analytics)
    return dataframes, enriched_df