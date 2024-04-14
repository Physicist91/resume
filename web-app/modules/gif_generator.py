import streamlit as st
import requests
import json

api_key = st.secrets["TENOR_API_KEY"]

def generate_random_gif(search_term = "job_search", format="mediumgif"):
    r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&limit=%s&media_filter=%s&random=%s" %\
                      (search_term, api_key, 1, format, "true"))
    if r.status_code == 200:
        gif = json.loads(r.content)
        url = gif['results'][0]['media_formats'][format]['url']
    else:
        url = None
    return url