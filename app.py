import streamlit as st
import os
import sqlalchemy as sa
import pandas as pd

# =================== Configurar Página ===================
st.set_page_config(page_title="TMDB App", page_icon="🎬", layout="wide")

# =================== Configuración de Base de Datos ===================
server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"
table_shows = "tmdb_shows_clean"
table_movies = "tmdb_movies_clean"

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

def filter_shows_or_movies(df, genre, title):
    """Filtra el DataFrame por género y título si están especificados."""
    if genre:
        df = df[df['genres'].str.contains(genre, case=False, na=False)]
    if title:
        column_name = 'original_name' if 'original_name' in df.columns else 'title'
        df = df[df[column_name].str.contains(title, case=False, na=False)]
    return df.sort_values(by='vote_average', ascending=False).head(10)

def display_results(results, content_type):
    """Muestra los resultados de series o películas."""
    if not results.empty:
        cols = st.columns(2)
        for i, row in enumerate(results.itertuples()):
            with cols[i % 2]:
                st.image(f"https://image.tmdb.org/t/p/w500{row.poster_path}", width=200)
                year = str(row.first_air_date)[:4] if content_type == "Series" and pd.notna(row.first_air_date) else str(row.release_date)[:4] if pd.notna(row.release_date) else "N/A"
                st.write(f"**{row.original_name if content_type == 'Series' else row.title} ({year})**")
                st.write(f"⭐ {row.vote_average} ({row.vote_count} votos)")
    else:
        st.warning(f"No se encontraron {content_type.lower()} para los filtros seleccionados.")

# =================== Control de navegación ===================
page = st.sidebar.radio("Navegación", ["Inicio", "Buscar Series", "Buscar Películas"])

# =================== Página de inicio ===================
if page == "Inicio":
    st.title("🎬 Bienvenido a la App de Búsqueda de Series y Películas TMDB")
    st.image("https://raw.githubusercontent.com/mikeismerio/tmdb_shows/main/home.jpg", use_column_width=True)
    st.markdown("### Selecciona una opción en el menú lateral para comenzar.")

# =================== Página de búsqueda de series ===================
elif page == "Buscar Series":
    st.title("🔍 Búsqueda de Series")
    genre_input = st.text_input("Introduce el Género (por ejemplo, 'Drama', 'Comedy'):")
    title_input = st.text_input("Introduce el Título (opcional):")

    if st.button("Buscar Series"):
        query = f"SELECT * FROM {table_shows} WHERE vote_average IS NOT NULL"
        shows = fetch_data(query)
        filtered_shows = filter_shows_or_movies(shows, genre_input, title_input)
        display_results(filtered_shows, "Series")

# =================== Página de búsqueda de películas ===================
elif page == "Buscar Películas":
    st.title("🎬 Búsqueda de Películas")
    genre_input = st.text_input("Introduce el Género (por ejemplo, 'Action', 'Horror'):")
    title_input = st.text_input("Introduce el Título (opcional):")

    if st.button("Buscar Películas"):
        query = f"SELECT * FROM {table_movies} WHERE vote_average IS NOT NULL"
        movies = fetch_data(query)
        filtered_movies = filter_shows_or_movies(movies, genre_input, title_input)
        display_results(filtered_movies, "Películas")
