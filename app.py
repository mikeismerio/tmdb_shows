import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página ===================
st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# =================== Imagen de portada ===================
PORTADA_URL = "https://raw.githubusercontent.com/mikeismerio/tmdb_shows/main/home.jpg"

# =================== Configuración de Base de Datos ===================
server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"
table_shows = "tmdb_shows_clean"
table_movies = "tmdb_movies_clean"

# Obtener credenciales desde variables de entorno (Streamlit Secrets)
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
        engine = sa.create_engine(
            connection_string,
            echo=False,
            connect_args={"autocommit": True}
        )
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

# =================== Función para mostrar resultados ===================
def mostrar_resultados(data, tipo="Series"):
    if not data.empty:
        cols = st.columns(2)
        for i, row in enumerate(data.itertuples()):
            with cols[i % 2]:
                st.image(f"https://image.tmdb.org/t/p/w500{row.poster_path}", width=200)
                year = str(row.first_air_date)[:4] if pd.notna(row.first_air_date) else "N/A"
                st.write(f"**{row.original_name if tipo == 'Series' else row.title} ({year})**")
    else:
        st.warning(f"No se encontraron {tipo.lower()} para los filtros seleccionados.")

# =================== Control de navegación ===================
current_page = st.sidebar.radio("Navegación", ["Inicio", "Buscar Series", "Buscar Películas"])

# =================== Página de Inicio ===================
if current_page == "Inicio":
    st.image(PORTADA_URL, use_container_width=True)
    st.markdown("## ¡Bienvenido a la plataforma de películas y series!")
    st.markdown("Selecciona una opción en el menú lateral.")

# =================== Página de Series ===================
elif current_page == "Buscar Series":
    st.header("Buscar Series")
    genre_input = st.sidebar.text_input("Género")
    title_input = st.sidebar.text_input("Título / Nombre Original")
    search_button = st.sidebar.button("Buscar Series")

    if search_button:
        query = f"SELECT TOP 10 * FROM {table_shows} WHERE vote_average IS NOT NULL ORDER BY vote_average DESC"
        data = fetch_data(query)

        # Aplicar filtros si es necesario
        if not data.empty:
            if genre_input:
                data = data[data['genres'].str.contains(genre_input, case=False, na=False)]
            if title_input:
                data = data[data['original_name'].str.contains(title_input, case=False, na=False)]

        mostrar_resultados(data, tipo="Series")

# =================== Página de Películas ===================
elif current_page == "Buscar Películas":
    st.header("Buscar Películas")
    genre_input = st.sidebar.text_input("Género")
    title_input = st.sidebar.text_input("Título")
    search_button = st.sidebar.button("Buscar Películas")

    if search_button:
        query = f"SELECT TOP 10 * FROM {table_movies} WHERE vote_average IS NOT NULL ORDER BY vote_average DESC"
        data = fetch_data(query)

        # Aplicar filtros si es necesario
        if not data.empty:
            if genre_input:
                data = data[data['genres'].str.contains(genre_input, case=False, na=False)]
            if title_input:
                data = data[data['title'].str.contains(title_input, case=False, na=False)]

        mostrar_resultados(data, tipo="Películas")
