import streamlit as st
import os

# Set page config
st.set_page_config(
    layout="wide"
)

hide_st_style="""
            <style>
            footer {visibility: hidden;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)

# Get the absolute path to the directory where this script is located
#current_dir = os.path.dirname(os.path.abspath(__file__))

page_1 = st.Page(
    "components/page_one.py",
    title="Home",
    icon=":material/home:"
)
page_2 = st.Page(
    "components/page_two.py", title="Gráfico", icon=":material/equalizer:"
)

pages = [page_1, page_2]
pg = st.navigation(pages)
pg.run()