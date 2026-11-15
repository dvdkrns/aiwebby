# streamlit run task1-template/app.py
# streamlit run app.py
import streamlit as st
from openai import OpenAI, AuthenticationError, OpenAIError

st.set_page_config(page_title="Meine KI-App")
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
st.title("My AI App")

prompt = st.text_area("Your Question")

if st.button("Submit", disabled=not prompt.strip()):
    try:
        with st.spinner("Answer is being created …"):
            response = client.chat.completions.create(
                model="google/gemma-4-E4B-it",
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

        st.write(response.choices[0].message.content)

    except AuthenticationError:
        st.error("API was not accept. Please check it.")

    except OpenAIError:
        st.error(
            "AI API request failed. Please check it and try again. "
        )

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
st.write("Hello, ", name, "! Are you ready to catch your first POKÉMON?")

# interactive field where people can enter their guess
guess = st.chat_input("Guess the POKÉMON!")
if guess:
    st.write(f"User has sent the following guess: {guess}")
