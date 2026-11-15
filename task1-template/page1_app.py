import streamlit as st
from openai import OpenAI, AuthenticationError, OpenAIError
import random

mapi = st.secrets.uos.API_UOS
# ── ask for API Key, stop if not yet provided  ────────────────────────────────────────────
with st.sidebar:
    api_key = st.text_input(
        "UOS AI API-Key",
        type="password",
        key="uos_api_key",
        placeholder="sk-...",
        autocomplete=mapi,
    ).strip()

if not api_key:
    st.info("Please enter your Uni Osnabrück API key. If you don't have one, you can obtain it from https://ai-keys.uni-osnabrueck.de.")
    st.stop()

# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key=api_key
)

# ── Main program logic starts here ────────────────────
#-------------------------------------------------------
# i wanted to center the title and caption which is not possiblie in Streamlit
# i used markdown instead and looked up how to center it
st.markdown(
    "<h1 style='text-align: center;'>The Guessing Game - POKÉMON edition!</h1>",
    unsafe_allow_html=True,
)

# playing around with the color 
st.markdown(
    "<p style='text-align: center; color: gray;'>This is the first task for the AI and the Web course aka for TurboTobyThomasThelen.</p>", 
    unsafe_allow_html=True,
)

# but I wanted to also use bold and color, plus have it centered 
st.markdown(''':gray[This is the first task for the] :gray[**AI and the Web**] :gray[ course.]''',
            text_alignment="center", 
            unsafe_allow_html=True,
)

# interactive field where people can enter their name
name = st.text_input("What's your name?", type="default", placeholder="Enter your name here")
# only shows after you enter your name 
if name not in ["", None]: 
    st.write("Hello, ", name, "! Are you ready to catch your first POKÉMON?")

# interactive field where people can enter their guess
guess = st.text_area("Guess the POKÉMON!")

# guessing game logic 
# generate a random pokemon using OpenAI (use the most prominent pokemons for that)
# if there is a guess, we can submit it
# we need to check if the guess is correct (if it is the correct pokemon)

if st.button("Submit", disabled=not guess.strip()):
    try:
        # not sure if we check it here???
        with st.spinner("Checking if your guess is correct..."):
            response = client.chat.completions.create(
                model="google/gemma-4-E4B-it",
                messages=[
                    {"role": "user", "content": guess},
                ],
            )

        st.write(response.choices[0].message.content)

    except AuthenticationError:
        st.error("API was not accepted. Please check it.")

    except OpenAIError:
        st.error(
            "AI API request failed. Please check it and try again. "
        )

if st.button("Go to page 2"):
    st.switch_page("page2_app.py")