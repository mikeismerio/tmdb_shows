import streamlit as st
from database import fetch_data
from utils import navigate, filter_top_shows

st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")

# Inicializar session_state si no existe
if "page" not in st.session_state:
    st.session_state.page = "home"
    st.session_state.selected_movie = None
if "search_genre" not in st.session_state:
    st.session_state.search_genre = ""

# Consultar datos de la base de datos
query = "SELECT * FROM tmdb_shows_clean"
df = fetch_data(query)

# Entrada de usuario
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
