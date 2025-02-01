import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página ===================
st.set_page_config(page_title="TMDB Buscador", page_icon="🎬", layout="wide")

# (Opcional: para depurar, mostramos la página actual)
st.write("Página actual:", st.session_state.get("page", "home"))

# =================== Configuración de Base de Datos ===================
server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"

# Tablas para series y películas
table_series = "tmdb_shows_clean"
table_movies = "tmdb_movies_clean"

# Credenciales (configuradas en Streamlit Secrets o variables de entorno)
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

connection_string = (
    f"mssql+pyodbc://{user}:{password}@{server}/{database}?"
    f"driver={driver}&Authentication=ActiveDirectoryPassword"
)

# =================== Funciones de Consulta y Filtrado ===================
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
        filtered = df[df['genres'].fillna('').str.contains(genre, case=False)]
        top = filtered.sort_values(by='vote_average', ascending=False).head(10)
        if not top.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top = top.copy()
            top['image_url'] = top['poster_path'].apply(lambda x: base_url + x if pd.notna(x) else None)
            return top[top['image_url'].notna()]
    return pd.DataFrame()

@st.cache_data
def filter_top_movies(df, genre):
    if genre:
        filtered = df[df['genres'].fillna('').str.contains(genre, case=False)]
        top = filtered.sort_values(by='vote_average', ascending=False).head(10)
        if not top.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top = top.copy()
            top['image_url'] = top['poster_path'].apply(lambda x: base_url + x if pd.notna(x) else None)
            return top[top['image_url'].notna()]
    return pd.DataFrame()

# =================== Inicialización de Variables de Sesión ===================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None
if "search_genre" not in st.session_state:
    st.session_state.search_genre = ""

# =================== Función de Navegación ===================
def navigate(page, item=None):
    st.session_state.page = page
    st.session_state.selected_item = item
    try:
        st.experimental_rerun()
    except Exception as e:
        st.write("Navegación actualizada, por favor interactúa nuevamente.")

# =================== Rutas/Páginas de la Aplicación ===================

# Página Principal (Menú)
if st.session_state.page == "home":
    st.title("Bienvenido")
    col1, col2 = st.columns(2)
    if col1.button("Buscar Series"):
        navigate("series")
    if col2.button("Buscar Películas"):
        navigate("movies")

# Página de Búsqueda de Series
elif st.session_state.page == "series":
    st.title("Buscar Series")
    query = f"SELECT * FROM {table_series}"
    df = fetch_data(query)
    genre_input = st.text_input("Introduce el Género para Series:", st.session_state.search_genre)
    if genre_input:
        st.session_state.search_genre = genre_input
        top_shows = filter_top_shows(df, genre_input)
        if not top_shows.empty:
            cols = st.columns(5)
            for index, row in top_shows.iterrows():
                with cols[index % 5]:
                    st.image(row["image_url"], use_column_width=True)
                    year = str(row["first_air_date"])[:4] if pd.notna(row["first_air_date"]) else "N/A"
                    if st.button(f"{row['name']} ({year})", key=f"series_{index}"):
                        navigate("series_details", row)
        else:
            st.info("No se encontraron series para ese género.")
    else:
        st.info("Introduce un género para buscar las Top 10 Series.")
    if st.button("Volver al Inicio"):
        navigate("home")

# Página de Búsqueda de Películas
elif st.session_state.page == "movies":
    st.title("Buscar Películas")
    query = f"SELECT * FROM {table_movies}"
    df = fetch_data(query)
    genre_input = st.text_input("Introduce el Género para Películas:", st.session_state.search_genre)
    if genre_input:
        st.session_state.search_genre = genre_input
        top_movies = filter_top_movies(df, genre_input)
        if not top_movies.empty:
            cols = st.columns(5)
            for index, row in top_movies.iterrows():
                with cols[index % 5]:
                    st.image(row["image_url"], use_column_width=True)
                    year = str(row["release_date"])[:4] if pd.notna(row["release_date"]) else "N/A"
                    if st.button(f"{row['title']} ({year})", key=f"movie_{index}"):
                        navigate("movies_details", row)
        else:
            st.info("No se encontraron películas para ese género.")
    else:
        st.info("Introduce un género para buscar las Top 10 Películas.")
    if st.button("Volver al Inicio"):
        navigate("home")

# Página de Detalles de una Serie
elif st.session_state.page == "series_details":
    series = st.session_state.selected_item
    if series is not None:
        base_url = "https://image.tmdb.org/t/p/w500"
        st.title(f"{series['name']}")
        if pd.notna(series.get("backdrop_path")):
            st.image(base_url + series["backdrop_path"], use_column_width=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            if pd.notna(series.get("poster_path")):
                st.image(base_url + series["poster_path"], width=250)
            else:
                st.write("No hay imagen disponible.")
        with col2:
            year = str(series["first_air_date"])[:4] if pd.notna(series["first_air_date"]) else "N/A"
            st.markdown(f"### {series['name']} ({year})")
            st.markdown(f"**Rating:** {series['vote_average']:.2f} ⭐ ({series['vote_count']} votos)")
            st.markdown(f"**Idioma:** {series.get('original_language', 'N/A').upper()}")
            st.markdown(f"**Géneros:** {series.get('genres', 'No disponible')}")
            st.markdown("### Descripción")
            st.markdown(series.get("overview", "No disponible"))
        if st.button("Volver a Series"):
            navigate("series")
    else:
        st.error("No se ha seleccionado ninguna serie.")

# Página de Detalles de una Película
elif st.session_state.page == "movies_details":
    movie = st.session_state.selected_item
    if movie is not None:
        base_url = "https://image.tmdb.org/t/p/w500"
        st.title(f"{movie['title']}")
        if pd.notna(movie.get("backdrop_path")):
            st.image(base_url + movie["backdrop_path"], use_column_width=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            if pd.notna(movie.get("poster_path")):
                st.image(base_url + movie["poster_path"], width=250)
            else:
                st.write("No hay imagen disponible.")
        with col2:
            year = str(movie["release_date"])[:4] if pd.notna(movie["release_date"]) else "N/A"
            st.markdown(f"### {movie['title']} ({year})")
            st.markdown(f"**Rating:** {movie['vote_average']:.2f} ⭐ ({movie['vote_count']} votos)")
            st.markdown(f"**Idioma:** {movie.get('original_language', 'N/A').upper()}")
            st.markdown(f"**Duración:** {movie.get('runtime', 'N/A')} minutos")
            st.markdown(f"**Géneros:** {movie.get('genres', 'No disponible')}")
            st.markdown("### Sinopsis")
            st.markdown(movie.get("overview", "No disponible"))
        if st.button("Volver a Películas"):
            navigate("movies")
    else:
        st.error("No se ha seleccionado ninguna película.")
