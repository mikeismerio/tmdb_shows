import sqlalchemy as sa
import pandas as pd
import streamlit as st

# Parámetros de conexión
#MOVIES
#nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com

#SHOWS
#nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com

server = "nwn7f7ze6vtuxen5age454nhca-colrz4odas5unhn7cagatohexq.datawarehouse.fabric.microsoft.com"
database = "TMDB"
driver = "ODBC Driver 17 for SQL Server"
user = "milton@cbtis70.edu.mx"
password = "dark6661882$"
table = "tmdb_shows_clean"

# Cadena de conexión
connection_string = (
    f"mssql+pyodbc://{user}:{password}@{server}/{database}?"
    f"driver={driver}&Authentication=ActiveDirectoryPassword"
)

@st.cache_data
def fetch_data(query):
    """Conecta a la base de datos y ejecuta una consulta."""
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
    """Filtra los datos según el género ingresado y los ordena de mayor a menor."""
    if genre:
        filtered_shows = df[df['genres'].str.contains(genre, case=False, na=False)]
        top_shows = filtered_shows.sort_values(by='vote_average', ascending=False).head(10)
        if not top_shows.empty:
            base_url = "https://image.tmdb.org/t/p/w500"
            top_shows['image_url'] = base_url + top_shows['poster_path']
            # Eliminar filas con valores nulos o no válidos en 'image_url'
            top_shows = top_shows[top_shows['image_url'].notna()]
            return top_shows
    return pd.DataFrame()

# Estilos CSS para mostrar detalles solo al hacer hover
st.markdown(
    """
    <style>
    .hover-effect {
        position: relative;
        display: inline-block;
        overflow: hidden;
        cursor: pointer;
        text-align: center;
    }
    .hover-effect img {
        display: block;
        max-width: 100%;
        height: auto;
    }
    .hover-effect .details {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        text-align: center;
        padding: 10px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .hover-effect:hover .details {
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App
st.title("Top 10 Shows por Género")

# Cargar los datos de la base
query = f"SELECT * FROM {table}"
df = fetch_data(query)

# Input para el género
genre_input = st.text_input("Introduce el Género:", "")

# Filtrar los resultados
if genre_input:
    top_shows = filter_top_shows(df, genre_input)
    if not top_shows.empty:
        st.markdown("### Top 10 Shows")
        # Usar 5 columnas por fila para imágenes más grandes
        cols_per_row = 5
        cols = st.columns(cols_per_row)
        for index, row in enumerate(top_shows.itertuples()):
            with cols[index % cols_per_row]:
                st.markdown(
                    f"""
                    <div class="hover-effect">
                        <img src="{row.image_url}" alt="{row.name}" />
                        <div class="details">
                            {row.name}<br>
                            Rating: {row.vote_average:.2f}<br>
                            Network: {row.networks if hasattr(row, 'networks') else 'N/A'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("No se encontraron resultados para el género ingresado.")
else:
    st.info("Introduce un género para buscar los Top 10 Shows.")
