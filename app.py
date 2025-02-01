import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página con Wide Mode ===================
st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# =================== Imagen de portada ===================
PORTADA_URL = "https://raw.githubusercontent.com/usuario/repositorio/rama/home.jpg"

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

def fetch_data(query):
    """Ejecuta una consulta SQL y devuelve un DataFrame"""
    try:
        engine = sa.create_engine(connection_string, echo=False, connect_args={"autocommit": True})
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

def navigate(page, item=None):
    st.session_state.page = page
    st.session_state.selected_item = item
    st.rerun()

def get_image_url(poster_path):
    """Devuelve la URL de la imagen o una imagen de marcador de posición."""
    if pd.notna(poster_path):
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/200?text=No+Image"

# =================== Control de Navegación ===================
if "page" not in st.session_state:
    st.session_state.page = "home"

# =================== Página Principal ===================
if st.session_state.page == "home":
    # Mostrar imagen de portada
    st.image(PORTADA_URL, use_column_width=True)
    st.markdown("## ¡Bienvenido! Usa los filtros de búsqueda para explorar series y películas.")

    st.sidebar.header("Filtros de Búsqueda")
    genre_input = st.sidebar.text_input("Género", "")
    title_input = st.sidebar.text_input("Título / Nombre Original", "")
    overview_input = st.sidebar.text_input("Descripción / Sinopsis", "")
    search_button = st.sidebar.button("Buscar")

    if search_button:
        query_movies = f"SELECT * FROM {table_movies} ORDER BY vote_average DESC"
        query_shows = f"SELECT * FROM {table_shows} ORDER BY vote_average DESC"

        movie_data = fetch_data(query_movies).head(10)
        show_data = fetch_data(query_shows).head(10)

        # Mostrar resultados de películas
        st.subheader("Resultados - Películas")
        if not movie_data.empty:
            cols_movies = st.columns(2)
            for i, row in enumerate(movie_data.itertuples()):
                with cols_movies[i % 2]:
                    st.image(get_image_url(row.poster_path), width=200)
                    year = str(row.release_date)[:4] if pd.notna(row.release_date) else "N/A"
                    if st.button(f"{row.title} ({year})", key=f"movie_{row.Index}"):
                        navigate("details", row._asdict())
        else:
            st.warning("No se encontraron películas para los filtros seleccionados.")

        # Mostrar resultados de series
        st.subheader("Resultados - Series")
        if not show_data.empty:
            cols_shows = st.columns(2)
            for i, row in enumerate(show_data.itertuples()):
                with cols_shows[i % 2]:
                    st.image(get_image_url(row.poster_path), width=200)
                    year = str(row.first_air_date)[:4] if pd.notna(row.first_air_date) else "N/A"
                    if st.button(f"{row.original_name} ({year})", key=f"show_{row.Index}"):
                        navigate("details", row._asdict())
        else:
            st.warning("No se encontraron series para los filtros seleccionados.")

# =================== Página de Detalles ===================
elif st.session_state.page == "details":
    if st.session_state.selected_item:
        item = st.session_state.selected_item
        base_url = "https://image.tmdb.org/t/p/w500"

        # Mostrar imagen de fondo
        if 'backdrop_path' in item and item['backdrop_path']:
            st.image(base_url + item['backdrop_path'], use_column_width=True)

        # Mostrar detalles en dos columnas
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(get_image_url(item.get('poster_path')), width=250)

        with col2:
            st.markdown(f"# {item.get('title', item.get('original_name', 'Desconocido'))}")
            st.markdown(f"**Rating:** {item.get('vote_average', 'N/A')} ⭐ ({item.get('vote_count', 0)} votos)")
            st.markdown(f"**Géneros:** {item.get('genres', 'No disponible')}")
            st.markdown(f"**Descripción:** {item.get('overview', 'No disponible')}")
            st.markdown(f"**Popularidad:** {item.get('popularity', 'N/A')}")
            st.markdown(f"**Idioma original:** {item.get('original_language', 'N/A').upper()}")

        # Botón para regresar a la lista
        if st.button("Volver a la lista"):
            navigate("home")
