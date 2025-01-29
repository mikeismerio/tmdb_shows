import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env o Streamlit Cloud
load_dotenv()

# Configuración de la base de datos
SERVER = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
DATABASE = "TMDB"
DRIVER = "ODBC Driver 17 for SQL Server"  # 🛠️ Cambiado a la versión 17
TABLE = "tmdb_shows_clean"

# Obtener credenciales desde variables de entorno (protegidas en Streamlit Cloud)
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")

# Cadena de conexión segura
CONNECTION_STRING = (
    f"mssql+pyodbc://{USER}:{PASSWORD}@{SERVER}/{DATABASE}?"
    f"driver={DRIVER}&Authentication=ActiveDirectoryPassword"
)
