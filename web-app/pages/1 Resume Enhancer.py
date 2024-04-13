import streamlit as st
import os

st.set_page_config(
        page_title="Resume Enhancer by ANUKS",
)

st.markdown("## Resume Enhancer")

if "form_filled" not in st.session_state:
    st.warning('Please input the form in the home page.', icon="⚠️")
else:
    st.write("blah")
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    st.write(os.environ["GOOGLE_API_KEY"] )
