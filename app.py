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

@st.cache_data
def filter_top_shows(df, genre):
    """Filtra y ordena las 10 mejores series según el género"""
    if genre:
        filtered_shows = df[df['genres'].str.contains(genre, case=False, na=False)]
        top_shows = filtered_shows.sort_values(by='vote_average', ascending=False).head(10)
        if not top_shows.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_shows['image_url'] = base_url + top_shows['poster_path']
            return top_shows[top_shows['image_url'].notna()]
    return pd.DataFrame()

@st.cache_data
def filter_top_movies(df, genre):
    """Filtra y ordena las 10 mejores películas según el género"""
    if genre:
        filtered_movies = df[df['genres'].str.contains(genre, case=False, na=False)]
        top_movies = filtered_movies.sort_values(by='vote_average', ascending=False).head(10)
        if not top_movies.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_movies['image_url'] = base_url + top_movies['poster_path']
            return top_movies[top_movies['image_url'].notna()]
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
    st.rerun()

# =================== Página Principal ===================
if st.session_state.page == "home":
    query_shows = f"SELECT * FROM {table_shows}"
    query_movies = f"SELECT * FROM {table_movies}"
    
    df_shows = fetch_data(query_shows)
    df_movies = fetch_data(query_movies)

    genre_input = st.text_input("Introduce el Género:", st.session_state.search_genre)

    if genre_input:
        st.session_state.search_genre = genre_input
        top_shows = filter_top_shows(df_shows, genre_input)
        top_movies = filter_top_movies(df_movies, genre_input)

        # ========== Mostrar Series ==========
        st.subheader("Top 10 Series")
        if not top_shows.empty:
            cols_per_row = 5
            cols = st.columns(cols_per_row)

            for index, row in enumerate(top_shows.itertuples()):
                with cols[index % cols_per_row]:
                    st.image(row.image_url, use_container_width=True)
                    
                    first_air_year = str(row.first_air_date)[:4] if hasattr(row, 'first_air_date') and row.first_air_date else "N/A"
                    
                    button_label = f"{row.name} ({first_air_year})"
                    if st.button(button_label, key=f"show_{row.Index}"):
                        navigate("details", row)
        else:
            st.warning("No se encontraron series para el género ingresado.")

        # ========== Mostrar Películas ==========
        st.subheader("Top 10 Películas")
        if not top_movies.empty:
            cols_per_row = 5
            cols = st.columns(cols_per_row)

            for index, row in enumerate(top_movies.itertuples()):
                with cols[index % cols_per_row]:
                    st.image(row.image_url, use_container_width=True)
                    
                    release_year = str(row.release_date)[:4] if hasattr(row, 'release_date') and row.release_date else "N/A"
                    
                    button_label = f"{row.title} ({release_year})"
                    if st.button(button_label, key=f"movie_{row.Index}"):
                        navigate("details", row)
        else:
            st.warning("No se encontraron películas para el género ingresado.")
    else:
        st.info("Introduce un género para buscar los Top 10 Shows y Películas.")

# =================== Página de Detalles ===================
elif st.session_state.page == "details":
    if st.session_state.selected_movie:
        movie = st.session_state.selected_movie
        base_url = "https://image.tmdb.org/t/p/w500"

        if hasattr(movie, 'backdrop_path') and movie.backdrop_path:
            st.image(base_url + movie.backdrop_path, use_column_width=True)

        col1, col2 = st.columns([1, 2])

        with col1:
            if hasattr(movie, 'poster_path') and movie.poster_path:
                st.image(base_url + movie.poster_path, width=250)
            else:
                st.warning("No hay imagen disponible.")

        with col2:
            st.markdown(f"# {movie.title if hasattr(movie, 'title') else movie.name} ({str(movie.release_date)[:4] if hasattr(movie, 'release_date') else 'N/A'})")
            st.markdown(f"**Rating:** {movie.vote_average:.2f} ⭐ ({movie.vote_count} votos)")
            st.markdown(f"**Idioma original:** {movie.original_language.upper() if hasattr(movie, 'original_language') else 'N/A'}")
            st.markdown(f"**Géneros:** {movie.genres if hasattr(movie, 'genres') else 'No disponible'}")
            st.markdown(f"### Descripción")
            st.markdown(movie.overview if hasattr(movie, 'overview') and movie.overview else "No disponible")

        st.markdown("---")

        if st.button("Volver a la lista"):
            navigate("home")
    else:
        st.warning("No se ha seleccionado ninguna serie o película.")
        if st.button("Volver a la lista"):
            navigate("home")
