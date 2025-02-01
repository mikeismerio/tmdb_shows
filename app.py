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
    """Ejecuta una consulta SQL y devuelve un DataFrame"""
    try:
        engine = sa.create_engine(
            connection_string,
            echo=False,
            connect_args={"autocommit": True},
        )
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

def build_query(table, genre, title, overview, network=None):
    """Construye una consulta SQL dinámica según los filtros seleccionados."""
    conditions = []
    
    if genre:
        conditions.append(f"genres LIKE '%{genre}%'")
    if title:
        conditions.append(f"title LIKE '%{title}%'")  # Para películas
        conditions.append(f"original_name LIKE '%{title}%'")  # Para series
    if overview:
        conditions.append(f"overview LIKE '%{overview}%'")
    if network and table == table_shows:
        conditions.append(f"networks LIKE '%{network}%'")

    where_clause = " AND ".join(conditions) if conditions else "1=1"  # Siempre válido si no hay filtros
    query = f"SELECT * FROM {table} WHERE {where_clause}"
    return query

# =================== Página Principal ===================
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate(page, movie=None):
    st.session_state.page = page
    st.session_state.selected_movie = movie
    st.rerun()

if st.session_state.page == "home":
    # ========= Mostrar portada si no hay búsqueda =========
    if "search_active" not in st.session_state or not st.session_state.search_active:
        st.image("https://via.placeholder.com/800x400.png?text=Bienvenido+a+la+Base+de+Pel%C3%ADculas+y+Series", use_column_width=True)
        st.markdown("## ¡Bienvenido! Usa los filtros de búsqueda para explorar series y películas.")

    # ========= Filtros de usuario =========
    st.sidebar.header("Filtros de Búsqueda")
    search_movies = st.sidebar.checkbox("Buscar Películas", value=True)
    search_shows = st.sidebar.checkbox("Buscar Series", value=True)

    genre_input = st.sidebar.text_input("Género", "")
    title_input = st.sidebar.text_input("Título / Nombre Original", "")
    overview_input = st.sidebar.text_input("Descripción / Sinopsis", "")

    # Botón para activar la búsqueda
    search_button = st.sidebar.button("Buscar")

    # Si se presiona "Buscar", construir consultas y traer datos
    if search_button:
        st.session_state.search_active = True

        # ========== Consultas dinámicas ==========
        if search_movies:
            movie_query = build_query(table_movies, genre_input, title_input, overview_input)
            movie_data = fetch_data(movie_query)

            st.subheader("Resultados - Películas")
            if not movie_data.empty:
                for _, row in movie_data.iterrows():
                    st.markdown(f"**{row['title']}** (Género: {row['genres']}, Rating: {row['vote_average']})")
                    if pd.notna(row['poster_path']):
                        st.image(f"https://image.tmdb.org/t/p/w500{row['poster_path']}", width=200)
            else:
                st.warning("No se encontraron películas para los filtros seleccionados.")

        if search_shows:
            show_query = build_query(table_shows, genre_input, title_input, overview_input)
            show_data = fetch_data(show_query)

            st.subheader("Resultados - Series")
            if not show_data.empty:
                for _, row in show_data.iterrows():
                    st.markdown(f"**{row['original_name']}** (Género: {row['genres']}, Rating: {row['vote_average']})")
                    if pd.notna(row['poster_path']):
                        st.image(f"https://image.tmdb.org/t/p/w500{row['poster_path']}", width=200)
            else:
                st.warning("No se encontraron series para los filtros seleccionados.")
