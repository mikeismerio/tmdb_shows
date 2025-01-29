import streamlit as st

def navigate(page, movie=None):
    """Función para cambiar de página en Streamlit"""
    st.session_state.page = page
    st.session_state.selected_movie = movie
    st.rerun()

def filter_top_shows(df, genre):
    """Filtra y ordena los 10 mejores shows según el género"""
    if genre:
        filtered_shows = df[df['genres'].str.contains(genre, case=False, na=False)]
        top_shows = filtered_shows.sort_values(by='vote_average', ascending=False).head(10)
        if not top_shows.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_shows['image_url'] = base_url + top_shows['poster_path']
            top_shows = top_shows[top_shows['image_url'].notna()]
            return top_shows
    return pd.DataFrame()
