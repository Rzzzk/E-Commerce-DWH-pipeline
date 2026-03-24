# Oracle Database Connection Properties
DB_USER = "pdb_admin"
DB_PASSWORD = "rzk1234" 
JDBC_URL = "jdbc:oracle:thin:@//localhost:1539/dwh_pdb"

def get_connection_properties():
    return {
        "user": DB_USER,
        "password": DB_PASSWORD,
        "driver": "oracle.jdbc.driver.OracleDriver"
    }