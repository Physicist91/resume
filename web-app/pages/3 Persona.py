import streamlit as st
from modules import gif_generator as gg


st.markdown("## Persona")
st.markdown("Feature coming soon...")
st.markdown("---")

gif_url = gg.generate_random_gif()
if gif_url:
    st.markdown("For now, here is a random gif for you: ")
    st.markdown("![Some random job gif :)]({})".format(gif_url))
