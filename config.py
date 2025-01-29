import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la base de datos
SERVER = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
DATABASE = "TMDB"
DRIVER = "ODBC Driver 18 for SQL Server"

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")

CONNECTION_STRING = (
    f"mssql+pyodbc://{USER}:{PASSWORD}@{SERVER}/{DATABASE}?"
    f"driver={DRIVER}&Authentication=ActiveDirectoryPassword"
)
