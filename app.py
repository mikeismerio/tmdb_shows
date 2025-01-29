import streamlit as st
from pages import home, details

# Controlador de navegación
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    home
elif st.session_state.page == "details":
    details
