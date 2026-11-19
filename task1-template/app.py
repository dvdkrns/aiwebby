# streamlit run task1-template/app.py
# streamlit run app.py
import streamlit as st

# title and icon of the browser tab
st.set_page_config(page_title="Pokémon Guessing Game", page_icon="🎮")

# Background: night sky fading into a grassy field; the content area gets a dark, see-through
# panel so the text stays readable. To use a picture instead, replace the gradient by
# url("https://...") or url("data:image/...").
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #1c2f6e 0%, #2f6db5 45%, #3f9142 88%, #2d6a30 100%) fixed; }
[data-testid="stHeader"] { background: transparent; }
.block-container { background: rgba(10, 20, 40, 0.6); border-radius: 16px; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# the two pages; each Page points to a file that is run when the page is open
page1 = st.Page("page1_app.py", title="Play", icon="🎮")
page2 = st.Page("page2_app.py", title="Stats", icon="📈")

pg = st.navigation(pages=[page1, page2])  # builds the page menu in the sidebar
pg.run()  # runs the page the user has selected
