import streamlit as st
from utils import navigate

st.set_page_config(page_title="Detalles", page_icon="📺", layout="wide")

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
