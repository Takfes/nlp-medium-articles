import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
import numpy as np
import requests
import config

USE_LOTTIE = True

# https://docs.streamlit.io/knowledge-base/tutorials/databases/mongodb
@st.experimental_singleton
def init_connection():
    return MongoClient(
    f"mongodb+srv://{config.MONGOUSER}:{config.MONGOPASS}@cluster0.v6cpwum.mongodb.net/?retryWrites=true&w=majority"
)

st.header('🪁 Data Science Articles 🧮')

# https://www.youtube.com/watch?v=apOw6WU-p4A
if USE_LOTTIE:
    def load_lottieur(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    lottie_animation_url = 'https://assets6.lottiefiles.com/packages/lf20_x62chJ.json'
    lottie_animation = load_lottieur(lottie_animation_url)

client = init_connection()
db = client['application']
col = db['articles']

# html_style = '<link href="styles.css" rel="stylesheet" />'
# html_container = """
#     <div class="container">
#     <div class="header">
#         <h4 class="header title">{title}</h4>
#     </div>
#     <br />
#     <div class="body">
#         <div class="body img">
#             <img src="{top_image}" />
#         </div>
#         <div class="body p">
#             <p>{summary}</p>
#         </div>
#     </div>
#     <br />
#     <div class="footer">
#         <span class="date">{publish_date}</span>
#         <span class="score">{score}</span>
#         <img
#         class="like" src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Facebook_Thumb_icon.svg/640px-Facebook_Thumb_icon.svg.png"
#         />
#     </div>
#     </div>
#     """

def fts(query, collection=col):
    return list(
        collection.aggregate(
            [
                {
                    "$search": {
                        "index": "application-articles-text",
                        "text": {
                            "query": query,
                            "path": {"wildcard": "*"}},
                    }
                },
                { 
                    "$project": { 
                        '_id': 0, 
                        'title': 1, 
                        'url': 1,
                        'top_image': 1,
                        'author' : 1,
                        'summary' : 1,
                        'text' : 1,
                        'publish_date' : 1,
                        'score': { '$meta': "searchScore" }}
                    }
            ]
        )
    )

user_query = st.sidebar.text_input('Query String')

if st.sidebar.button('Search'):
    results = fts(user_query, collection=col)
    st.sidebar.write(f'Total Results : {len(results)}')
    col1, col2 = st.columns([3,1])
    center, side = results[:10], results[10:30]
    # html_results = html_style
    for q in center:
        # html_results += html_container.format(
        #     title=q.get('title'),
        #     top_image=q.get('top_image'),
        #     summary=q.get('summary'),
        #     publish_date=q.get('publish_date'),
        #     score=round(q.get('score'),2),
        # )
        col1.markdown(f"""* [{q.get('title')}]({q.get('url')})""")
        col1.markdown(f"{q.get('summary')[:100]}...")
        col1.markdown(f"> published on {q.get('publish_date')}   |   {q.get('score'):.2f}")
        col1.markdown("- - -")
    # components.html(html_results,height=600)
    for q in side:
        # col2.write(q)
        col2.markdown(f"""* [{q.get('title')}]({q.get('url')})""")
else :
    if USE_LOTTIE:
        st_lottie(lottie_animation)
