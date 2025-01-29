import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página con Wide Mode ===================
st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# =================== Configuración de Base de Datos ===================
server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"  # ✅ Usa ODBC 17
table = "tmdb_shows_clean"

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
    """Filtra y ordena los 10 mejores shows según el género"""
    if genre:
        filtered_shows = df[df['genres'].str.contains(genre, case=False, na=False)]
        top_shows = filtered_shows.sort_values(by='vote_average', ascending=False).head(10)
        if not top_shows.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_shows['image_url'] = base_url + top_shows['poster_path']
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
    st.rerun()

# =================== Página Principal ===================
if st.session_state.page == "home":
    query = f"SELECT * FROM {table}"
    df = fetch_data(query)

    genre_input = st.text_input("Introduce el Género:", st.session_state.search_genre)

    if genre_input:
        st.session_state.search_genre = genre_input
        top_shows = filter_top_shows(df, genre_input)

        if not top_shows.empty:
            cols_per_row = 5
            cols = st.columns(cols_per_row)

            for index, row in enumerate(top_shows.itertuples()):
                with cols[index % cols_per_row]:
                    st.image(row.image_url, use_container_width=True)
                    button_label = f"{row.name} ({row.first_air_date[:4] if hasattr(row, 'first_air_date') else 'N/A'})"
                    if st.button(button_label, key=row.Index):
                        navigate("details", row)
        else:
            st.warning("No se encontraron resultados para el género ingresado.")
    else:
        st.info("Introduce un género para buscar los Top 10 Shows.")

# =================== Página de Detalles ===================
elif st.session_state.page == "details":
    if st.session_state.selected_movie:
        movie = st.session_state.selected_movie
        base_url = "https://image.tmdb.org/t/p/w500"

        if hasattr(movie, 'backdrop_path') and movie.backdrop_path:
            st.image(base_url + movie.backdrop_path, use_column_width=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(movie.image_url, width=250)

        with col2:
            st.markdown(f"# {movie.name} ({movie.first_air_date[:4] if hasattr(movie, 'first_air_date') else 'N/A'})")
            st.markdown(f"**Rating:** {movie.vote_average:.2f} ⭐ ({movie.vote_count} votos)")
            st.markdown(f"**Idioma original:** {movie.original_language.upper()}")
            st.markdown(f"**Géneros:** {movie.genres if hasattr(movie, 'genres') else 'No disponible'}")
            st.markdown(f"### Descripción")
            st.markdown(movie.overview if hasattr(movie, 'overview') else "No disponible")

        if st.button("Volver a la lista"):
            navigate("home")
    else:
        st.warning("No se ha seleccionado ninguna serie.")
        if st.button("Volver a la lista"):
            navigate("home")
