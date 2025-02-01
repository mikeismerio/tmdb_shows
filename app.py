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

def apply_filters(df, title, overview, genre, network=None):
    """Aplica filtros usando str.contains en el DataFrame."""
    if title.strip():
        df = df[df['title'].str.contains(title, case=False, na=False) | df['original_name'].str.contains(title, case=False, na=False)]
    if overview.strip():
        df = df[df['overview'].str.contains(overview, case=False, na=False)]
    if genre.strip():
        df = df[df['genres'].str.contains(genre, case=False, na=False)]
    if network and 'networks' in df.columns:
        df = df[df['networks'].str.contains(network, case=False, na=False)]
    return df

def navigate(page, item=None):
    st.session_state.page = page
    st.session_state.selected_item = item
    st.rerun()

def get_image_url(poster_path):
    """Devuelve la URL de la imagen o una imagen de marcador de posición."""
    if pd.notna(poster_path):
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/200?text=No+Image"

# =================== Página Principal ===================
if "page" not in st.session_state:
    st.session_state.page = "home"

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
    network_input = None

    if search_shows:
        network_input = st.sidebar.text_input("Network (Para series)")

    # Mostrar campo adicional para excluir contenido adulto solo si se busca películas
    exclude_adult = None
    if search_movies:
        exclude_adult = st.sidebar.checkbox("Excluir contenido adulto", value=True)

    # Botón para activar la búsqueda
    search_button = st.sidebar.button("Buscar")

    # Si se presiona "Buscar", construir consultas y traer datos
    if search_button:
        st.session_state.search_active = True

        # ========== Consultas dinámicas ==========
        if search_movies:
            movie_query = f"SELECT * FROM {table_movies} ORDER BY vote_average DESC"
            movie_data = fetch_data(movie_query)

            # Aplicar filtro de contenido adulto si es necesario
            if exclude_adult is not None:
                movie_data = movie_data[movie_data['adult'] == (0 if exclude_adult else 1)]

            # Aplicar filtros usando str.contains()
            movie_data = apply_filters(movie_data, title_input, overview_input, genre_input)

            movie_data = movie_data.head(10)  # Limitar a los primeros 10 resultados

            st.subheader("Resultados - Películas")
            if not movie_data.empty:
                cols = st.columns(2)  # Mostrar en 2 columnas
                for i, row in enumerate(movie_data.itertuples()):
                    year = str(row.release_date)[:4] if pd.notna(row.release_date) else "N/A"
                    with cols[i % 2]:  # Alternar entre columnas
                        st.image(get_image_url(row.poster_path), width=200)
                        if st.button(f"{row.title} ({year})", key=f"movie_{row.Index}"):
                            navigate("details", row._asdict())  # Pasar datos como diccionario

            else:
                st.warning("No se encontraron películas para los filtros seleccionados.")

        if search_shows:
            show_query = f"SELECT * FROM {table_shows} ORDER BY vote_average DESC"
            show_data = fetch_data(show_query)

            # Aplicar filtros usando str.contains()
            show_data = apply_filters(show_data, title_input, overview_input, genre_input, network=network_input)

            show_data = show_data.head(10)  # Limitar a los primeros 10 resultados

            st.subheader("Resultados - Series")
            if not show_data.empty:
                cols = st.columns(2)  # Mostrar en 2 columnas
                for i, row in enumerate(show_data.itertuples()):
                    year = str(row.first_air_date)[:4] if pd.notna(row.first_air_date) else "N/A"
                    with cols[i % 2]:  # Alternar entre columnas
                        st.image(get_image_url(row.poster_path), width=200)
                        if st.button(f"{row.original_name} ({year})", key=f"show_{row.Index}"):
                            navigate("details", row._asdict())  # Pasar datos como diccionario

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

        # Información detallada
        st.markdown(f"## {item['title'] if 'title' in item else item['original_name']}")
        st.markdown(f"**Rating:** {item['vote_average']} ⭐ ({item['vote_count']} votos)")
        st.markdown(f"**Géneros:** {item['genres']}")
        st.markdown(f"**Descripción:** {item['overview'] if pd.notna(item['overview']) else 'No disponible'}")

        # Botón para regresar a la lista
        if st.button("Volver a la lista"):
            navigate("home")
