import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página con Wide Mode ===================
st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# =================== Configuración de Base de Datos ===================
server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"
table = "tmdb_shows_clean"

# Credenciales (configuradas en Streamlit Secrets o variables de entorno)
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

connection_string = (
    f"mssql+pyodbc://{user}:{password}@{server}/{database}?"
    f"driver={driver}&Authentication=ActiveDirectoryPassword"
)

@st.cache_data
def fetch_data(query):
    try:
        engine = sa.create_engine(connection_string, echo=False, connect_args={"autocommit": True})
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

@st.cache_data
def filter_top_shows(df, genre):
    if genre:
        filtered_shows = df[df['genres'].fillna('').str.contains(genre, case=False)]
        top_shows = filtered_shows.sort_values(by='vote_average', ascending=False).head(10)
        if not top_shows.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_shows = top_shows.copy()
            top_shows['image_url'] = top_shows['poster_path'].apply(lambda x: base_url + x if pd.notna(x) else None)
            return top_shows[top_shows['image_url'].notna()]
    return pd.DataFrame()

# =================== Control de Navegación ===================
if "page" not in st.session_state:
    st.session_state.page = "home"
    st.session_state.selected_movie = None
if "search_genre" not in st.session_state:
    st.session_state.search_genre = ""

def navigate(page, movie=None):
    st.session_state.page = page
    st.session_state.selected_movie = movie
    # Opción 1: Si actualizaste Streamlit, puedes usar:
    # st.experimental_rerun()
    # Opción 2: Simplemente omite el rerun, ya que la interacción del botón reinicia el script.
    # return  (la función termina aquí)

# =================== Página Principal ===================
if st.session_state.page == "home":
    st.title("Bienvenido")
    col1, col2 = st.columns(2)
    if col1.button("Buscar Series"):
        navigate("series")
    if col2.button("Buscar Películas"):
        navigate("movies")

# (El resto de tu código, que incluye la página de búsqueda y detalles, se mantendría similar)
