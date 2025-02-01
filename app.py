import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página ===================
st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# =================== Configuración de Base de Datos ===================
server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"

# Tablas para series y películas
table_series = "tmdb_shows_clean"
table_movies = "tmdb_movies_clean"

# Credenciales desde variables de entorno (Streamlit Secrets)
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

connection_string = (
    f"mssql+pyodbc://{user}:{password}@{server}/{database}?"
    f"driver={driver}&Authentication=ActiveDirectoryPassword"
)

# =================== Funciones para Conexión y Filtrado ===================
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

@st.cache_data
def filter_top_shows(df, genre):
    """Filtra y ordena las 10 mejores series según el género"""
    if genre:
        filtered_shows = df[df['genres'].fillna('').str.contains(genre, case=False)]
        top_shows = filtered_shows.sort_values(by='vote_average', ascending=False).head(10)
        if not top_shows.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_shows = top_shows.copy()  # Evitar advertencias de modificación
            top_shows['image_url'] = top_shows['poster_path'].apply(
                lambda x: base_url + x if pd.notna(x) else None
            )
            return top_shows[top_shows['image_url'].notna()]
    return pd.DataFrame()

@st.cache_data
def filter_top_movies(df, genre):
    """Filtra y ordena las 10 mejores películas según el género"""
    if genre:
        filtered_movies = df[df['genres'].fillna('').str.contains(genre, case=False)]
        top_movies = filtered_movies.sort_values(by='vote_average', ascending=False).head(10)
        if not top_movies.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_movies = top_movies.copy()
            top_movies['image_url'] = top_movies['poster_path'].apply(
                lambda x: base_url + x if pd.notna(x) else None
            )
            return top_movies[top_movies['image_url'].notna()]
    return pd.DataFrame()

# =================== Control de Navegación ===================
# Usamos una variable de sesión para controlar la página actual y el ítem seleccionado.
if "page" not in st.session_state:
    st.session_state.page = "home"       # Página principal con botones
    st.session_state.selected_item = None  # Ítem (serie o película) seleccionado
if "search_genre" not in st.session_state:
    st.session_state.search_genre = ""

def navigate(page, item=None):
    st.session_state.page = page
    st.session_state.selected_item = item
    st.experimental_rerun()

# =================== PÁGINAS DE LA APLICACIÓN ===================

# --- Página Principal: Menú ---
if st.session_state.page == "home":
    st.title("Bienvenido")
    st.write("Elige lo que deseas buscar:")
    col1, col2 = st.columns(2)
    if col1.button("Buscar Series"):
        navigate("series")
    if col2.button("Buscar Películas"):
        navigate("movies")

# --- Página de Búsqueda de Series ---
elif st.session_state.page == "series":
    st.title("Buscar Series")
    query = f"SELECT * FROM {table_series}"
    df = fetch_data(query)
    genre_input = st.text_input("Introduce el Género para Series:", st.session_state.search_genre)
    if genre_input:
        st.session_state.search_genre = genre_input
        top_shows = filter_top_shows(df, genre_input)
        if not top_shows.empty:
            cols_per_row = 5
            cols = st.columns(cols_per_row)
            for index, row in top_shows.iterrows():
                with cols[index % cols_per_row]:
                    st.image(row['image_url'], use_column_width=True)
                    # Se extrae el año a partir de 'first_air_date'
                    first_air_year = str(row['first_air_date'])[:4] if pd.notna(row['first_air_date']) else "N/A"
                    # Se asume que la columna del nombre es "name"
                    button_label = f"{row['name']} ({first_air_year})"
                    if st.button(button_label, key=f"series_{index}"):
                        navigate("series_details", row)
        else:
            st.warning("No se encontraron resultados para el género ingresado.")
    else:
        st.info("Introduce un género para buscar las Top 10 Series.")
    if st.button("Volver al Inicio"):
        navigate("home")

# --- Página de Búsqueda de Películas ---
elif st.session_state.page == "movies":
    st.title("Buscar Películas")
    query = f"SELECT * FROM {table_movies}"
    df = fetch_data(query)
    genre_input = st.text_input("Introduce el Género para Películas:", st.session_state.search_genre)
    if genre_input:
        st.session_state.search_genre = genre_input
        top_movies = filter_top_movies(df, genre_input)
        if not top_movies.empty:
            cols_per_row = 5
            cols = st.columns(cols_per_row)
            for index, row in top_movies.iterrows():
                with cols[index % cols_per_row]:
                    st.image(row['image_url'], use_column_width=True)
                    release_year = str(row['release_date'])[:4] if pd.notna(row['release_date']) else "N/A"
                    button_label = f"{row['title']} ({release_year})"
                    if st.button(button_label, key=f"movie_{index}"):
                        navigate("movies_details", row)
        else:
            st.warning("No se encontraron resultados para el género ingresado.")
    else:
        st.info("Introduce un género para buscar las Top 10 Películas.")
    if st.button("Volver al Inicio"):
        navigate("home")

# --- Página de Detalles de una Serie ---
elif st.session_state.page == "series_details":
    if st.session_state.selected_item is not None:
        series = st.session_state.selected_item
        base_url = "https://image.tmdb.org/t/p/w500"
        st.title(f"{series['name']}")  # Se asume columna "name"
        if pd.notna(series.get('backdrop_path')):
            st.image(base_url + series['backdrop_path'], use_column_width=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            if pd.notna(series.get('poster_path')):
                st.image(base_url + series['poster_path'], width=250)
            else:
                st.warning("No hay imagen disponible.")
        with col2:
            first_air_year = str(series['first_air_date'])[:4] if pd.notna(series['first_air_date']) else "N/A"
            st.markdown(f"# {series['name']} ({first_air_year})")
            st.markdown(f"**Rating:** {series['vote_average']:.2f} ⭐ ({series['vote_count']} votos)")
            st.markdown(
                f"**Idioma original:** {series['original_language'].upper()}" if series.get('original_language') else "**Idioma original:** N/A"
            )
            st.markdown(
                f"**Número de temporadas:** {series['number_of_seasons']}" if 'number_of_seasons' in series and pd.notna(series['number_of_seasons']) else "**Número de temporadas:** N/A"
            )
            st.markdown(
                f"**Número de episodios:** {series['number_of_episodes']}" if 'number_of_episodes' in series and pd.notna(series['number_of_episodes']) else "**Número de episodios:** N/A"
            )
            st.markdown(
                f"**Popularidad:** {series['popularity']}" if series.get('popularity') else "**Popularidad:** N/A"
            )
            st.markdown(
                f"**Estado:** {series['status']}" if series.get('status') else "**Estado:** N/A"
            )
            st.markdown(
                f"**En producción:** {'Sí' if series.get('in_production') else 'No'}"
            )
            st.markdown(
                f"**Géneros:** {series['genres']}" if series.get('genres') else "**Géneros:** No disponible"
            )
            st.markdown(
                f"**Creador(es):** {series['created_by']}" if series.get('created_by') else "**Creador(es):** No disponible"
            )
            st.markdown("### Descripción")
            st.markdown(series['overview'] if series.get('overview') else "No disponible")
        if st.button("Volver a Series"):
            navigate("series")
    else:
        st.warning("No se ha seleccionado ninguna serie.")
        if st.button("Volver a Series"):
            navigate("series")

# --- Página de Detalles de una Película ---
elif st.session_state.page == "movies_details":
    if st.session_state.selected_item is not None:
        movie = st.session_state.selected_item
        base_url = "https://image.tmdb.org/t/p/w500"
        st.title(f"{movie['title']}")
        if pd.notna(movie.get('backdrop_path')):
            st.image(base_url + movie['backdrop_path'], use_column_width=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            if pd.notna(movie.get('poster_path')):
                st.image(base_url + movie['poster_path'], width=250)
            else:
                st.warning("No hay imagen disponible.")
        with col2:
            release_year = str(movie['release_date'])[:4] if pd.notna(movie['release_date']) else "N/A"
            st.markdown(f"# {movie['title']} ({release_year})")
            st.markdown(f"**Rating:** {movie['vote_average']:.2f} ⭐ ({movie['vote_count']} votos)")
            st.markdown(
                f"**Idioma original:** {movie['original_language'].upper()}" if movie.get('original_language') else "**Idioma original:** N/A"
            )
            st.markdown(
                f"**Duración:** {movie['runtime']} minutos" if pd.notna(movie['runtime']) else "**Duración:** N/A"
            )
            st.markdown(
                f"**Popularidad:** {movie['popularity']}" if pd.notna(movie['popularity']) else "**Popularidad:** N/A"
            )
            st.markdown(
                f"**Estado:** {movie['status']}" if movie.get('status') else "**Estado:** N/A"
            )
            st.markdown(
                f"**Géneros:** {movie['genres']}" if movie.get('genres') else "**Géneros:** No disponible"
            )
            st.markdown("### Sinopsis")
            st.markdown(movie['overview'] if movie.get('overview') else "No disponible")
        if st.button("Volver a Películas"):
            navigate("movies")
    else:
        st.warning("No se ha seleccionado ninguna película.")
        if st.button("Volver a Películas"):
            navigate("movies")
