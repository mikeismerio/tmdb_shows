import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página ===================
st.set_page_config(page_title="TMDB Shows", page_icon="🎬", layout="wide")

# =================== Configuración de Base de Datos ===================
server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"
table = "tmdb_shows_clean"

# Obtener credenciales desde variables de entorno
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

# Cadena de conexión
connection_string = (
    f"mssql+pyodbc://{user}:{password}@{server}/{database}?"
    f"driver={driver}&Authentication=ActiveDirectoryPassword"
)

@st.cache_data
def fetch_data(query):
    """Ejecuta una consulta SQL y devuelve un DataFrame."""
    try:
        engine = sa.create_engine(connection_string, echo=False, connect_args={"autocommit": True})
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

def filter_shows(genre):
    """Obtiene y filtra los shows por género."""
    query = f"SELECT * FROM {table} WHERE vote_average IS NOT NULL"
    data = fetch_data(query)
    
    if not data.empty and genre:
        # Aplicar filtro por género si está especificado
        data = data[data['genres'].str.contains(genre, case=False, na=False)]
    
    # Ordenar por calificación y tomar los 10 mejores resultados
    return data.sort_values(by='vote_average', ascending=False).head(10)

def display_shows(shows):
    """Muestra los resultados de los shows en Streamlit."""
    if not shows.empty:
        cols = st.columns(2)  # 2 columnas para mostrar las imágenes
        for i, row in enumerate(shows.itertuples()):
            with cols[i % 2]:
                st.image(f"https://image.tmdb.org/t/p/w500{row.poster_path}", width=200)
                year = str(row.first_air_date)[:4] if pd.notna(row.first_air_date) else "N/A"
                st.write(f"**{row.original_name} ({year})**")
                st.write(f"⭐ {row.vote_average} ({row.vote_count} votos)")
    else:
        st.warning("No se encontraron resultados para el género especificado.")

# =================== Página principal ===================
st.title("🎬 Búsqueda de Series TMDB")
genre_input = st.text_input("Introduce el Género para buscar series (por ejemplo, 'Drama', 'Action', etc.):")

if st.button("Buscar"):
    # Filtrar y mostrar resultados
    top_shows = filter_shows(genre_input)
    display_shows(top_shows)
