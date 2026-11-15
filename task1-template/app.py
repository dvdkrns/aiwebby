# streamlit run task1-template/app.py
# streamlit run app.py
import streamlit as st

page1 = st.Page("page1_app.py", title="Guessing Game", icon="🤔")
page2 = st.Page("page2_app.py", title="Stats", icon="📈")

pg = st.navigation(pages=[page1, page2])
pg.run()

