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
# guessing game logic 
# generate a random pokemon using OpenAI (use the most famous pokemons for that)
if "pokemon" not in st.session_state:
    with st.spinner("Generating a random POKÉMON..."):
        response = client.chat.completions.create(
            model="google/gemma-4-E4B-it",
            messages=[
                {"role": "user", "content": "Generate a random POKÉMON from the first generation (1-151) and return only its name."
                }
            ],
        )
    st.session_state["pokemon"] = response.choices[0].message.content.strip()
    st.info("A new POKÉMON has been generated! Try to guess it.")

# if there is a guess, we can submit it
if guess.strip():
    st.write(f"You guessed: {guess}")
    # we need to check if the guess is correct 
    if guess.strip().lower() == st.session_state["pokemon"].lower():
        st.success("Congratulations! You guessed the correct POKÉMON!")
        del st.session_state["pokemon"]  # reset for a new game
    else:
        st.error("Sorry, that's not the correct POKÉMON. Try again!")

# if the player guesses wrong 3x, we give them a hint
# we can tell them what color the pokemon is, or what type it is

# if the guess is not correct, we give the option to reset the game and generate a new pokemon.
if st.button("Reset", type="primary"):
    del st.session_state["pokemon"]
    st.info("The game has been reset. A new POKÉMON will be generated on your next guess.")

# update data structures for statistics and chat view (counting guesses, perhaps maintaining a history etc.


if st.button("Go to page 2"):
    st.switch_page("page2_app.py")