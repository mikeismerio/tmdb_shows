import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página con Wide Mode ===================
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

def fetch_data(query):
    """Ejecuta una consulta SQL y devuelve un DataFrame."""
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

# =================== Inicialización del estado ===================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "genre_input" not in st.session_state:
    st.session_state.genre_input = ""
if "title_input" not in st.session_state:
    st.session_state.title_input = ""
if "overview_input" not in st.session_state:
    st.session_state.overview_input = ""
if "exclude_adult" not in st.session_state:
    st.session_state.exclude_adult = True

# =================== Página de Inicio ===================
if st.session_state.page == "home":
    st.image(PORTADA_URL, use_container_width=True)
    st.markdown("## ¡Bienvenido a la plataforma de películas y series!")
    st.markdown("Selecciona una de las opciones a continuación:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Buscar Series"):
            navigate("series")
    with col2:
        if st.button("Buscar Películas"):
            navigate("movies")

# =================== Página de Series ===================
elif st.session_state.page == "series":
    st.header("Buscar Series")
    st.sidebar.header("Filtros de Búsqueda (Series)")
    st.session_state.genre_input = st.sidebar.text_input("Género", st.session_state.genre_input)
    st.session_state.title_input = st.sidebar.text_input("Título / Nombre Original", st.session_state.title_input)
    st.session_state.overview_input = st.sidebar.text_input("Descripción / Sinopsis", st.session_state.overview_input)
    search_button = st.sidebar.button("Buscar Series")

    if search_button:
        # Consulta SQL optimizada
        show_query = f"""
        SELECT TOP 10 * 
        FROM {table_shows} 
        WHERE vote_average IS NOT NULL 
        ORDER BY vote_average DESC
        """
        show_data = fetch_data(show_query)

        # Aplicar filtros usando str.contains (si los filtros no están vacíos)
        if not show_data.empty:
            show_data = show_data[
                (show_data['genres'].str.contains(st.session_state.genre_input, case=False, na=False) if st.session_state.genre_input else True) &
                (show_data['original_name'].str.contains(st.session_state.title_input, case=False, na=False) if st.session_state.title_input else True) &
                (show_data['overview'].str.contains(st.session_state.overview_input, case=False, na=False) if st.session_state.overview_input else True)
            ]

        # Mostrar resultados de series
        if not show_data.empty:
            st.subheader("Resultados - Series")
            cols_shows = st.columns(2)
            for i, row in enumerate(show_data.itertuples()):
                with cols_shows[i % 2]:
                    st.image(get_image_url(row.poster_path), width=200)
                    year = str(row.first_air_date)[:4] if pd.notna(row.first_air_date) else "N/A"
                    if st.button(f"{row.original_name} ({year})", key=f"show_{row.Index}"):
                        navigate("details", row._asdict())
        else:
            st.warning("No se encontraron series para los filtros seleccionados.")

    if st.button("Volver a la Página Principal"):
        navigate("home")

# =================== Página de Películas ===================
elif st.session_state.page == "movies":
    st.header("Buscar Películas")
    st.sidebar.header("Filtros de Búsqueda (Películas)")
    st.session_state.genre_input = st.sidebar.text_input("Género", st.session_state.genre_input)
    st.session_state.title_input = st.sidebar.text_input("Título", st.session_state.title_input)
    st.session_state.overview_input = st.sidebar.text_input("Descripción / Sinopsis", st.session_state.overview_input)
    st.session_state.exclude_adult = st.sidebar.checkbox("Excluir contenido adulto", value=True)
    search_button = st.sidebar.button("Buscar Películas")

    if search_button:
        # Consulta SQL optimizada
        movie_query = f"""
        SELECT TOP 10 * 
        FROM {table_movies} 
        WHERE vote_average IS NOT NULL 
        ORDER BY vote_average DESC
        """
        movie_data = fetch_data(movie_query)

        # Aplicar filtros usando str.contains (si los filtros no están vacíos)
        if not movie_data.empty:
            movie_data = movie_data[
                (movie_data['genres'].str.contains(st.session_state.genre_input, case=False, na=False) if st.session_state.genre_input else True) &
                (movie_data['title'].str.contains(st.session_state.title_input, case=False, na=False) if st.session_state.title_input else True) &
                (movie_data['overview'].str.contains(st.session_state.overview_input, case=False, na=False) if st.session_state.overview_input else True)
            ]
            if st.session_state.exclude_adult:
                movie_data = movie_data[movie_data['adult'] == 0]

        # Mostrar resultados de películas
        if not movie_data.empty:
            st.subheader("Resultados - Películas")
            cols_movies = st.columns(2)
            for i, row in enumerate(movie_data.itertuples()):
                with cols_movies[i % 2]:
                    st.image(get_image_url(row.poster_path), width=200)
                    year = str(row.release_date)[:4] if pd.notna(row.release_date) else "N/A"
                    if st.button(f"{row.title} ({year})", key=f"movie_{row.Index}"):
                        navigate("details", row._asdict())
        else:
            st.warning("No se encontraron películas para los filtros seleccionados.")

    if st.button("Volver a la Página Principal"):
        navigate("home")

# =================== Página de Detalles ===================
elif st.session_state.page == "details":
    if st.session_state.selected_item:
        item = st.session_state.selected_item
        base_url = "https://image.tmdb.org/t/p/w500"

        # Mostrar imagen de fondo si está disponible
        if item.get('backdrop_path'):
            st.image(base_url + item['backdrop_path'], use_container_width=True)

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
        if st.button("Volver a la Página Principal"):
            navigate("home")
