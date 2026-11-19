# ══ PLAY PAGE: guess the secret Pokémon ═══════════════════════════════════════════════════
# Streamlit runs this whole file from top to bottom on EVERY interaction (a "rerun").
# Everything that must survive a rerun lives in st.session_state:
#   secret     the secret Pokémon as English slug, e.g. "charizard" (also used for image/types)
#   messages   chat history: list of {"role": "user" | "assistant", "content": text}
#   guesses    guesses of the current round: list of {"guess", "quality", "reason"}
#   questions  number of questions asked in the current round
#   result     None while playing, then "won" or "lost"
#   score      points of the current winning streak (reset when the player gives up)
#   highscore  best score so far
#   games      all finished rounds - the Stats page reads this list

import random
import requests
import streamlit as st
from openai import OpenAI, AuthenticationError, OpenAIError
from pokemon_data import (POKEMON, NAMES_DE, IMAGE_URL, SPRITE_URL,
                          display_name, get_types, get_facts, suggest)

# ── 1. API key ────────────────────────────────────────────────────────────────────────────
mapi = st.secrets.uos.API_UOS  # from .streamlit/secrets.toml:  [uos]  API_UOS = "sk-..."
with st.sidebar:
    api_key = st.text_input(
        "UOS AI API-Key",
        type="password",
        key="uos_api_key",
        placeholder="sk-...",
        autocomplete=mapi,
    ).strip()

# without a key the rest of the page is not drawn
if not api_key:
    st.info("Please enter your Uni Osnabrück API key. If you don't have one, you can obtain it from https://ai-keys.uni-osnabrueck.de.")
    st.stop()

# the client talks to the university's AI server; ask_professor() below uses it
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key=api_key
)

# ── 2. Game logic: functions that change the game state ───────────────────────────────────
MODEL = "google/gemma-4-E4B-it"  # the LLM of the university server
PARTNERS = ["pikachu", "bulbasaur", "charmander", "squirtle", "eevee"]  # choices for the player avatar


def guess_quality(guess, secret):
    """Estimate how close a guess was (0-100) by comparing the types of both Pokémon.
    Returns (score, reason); score is None if the types could not be loaded."""
    if guess == secret:
        return 100, "correct Pokémon"
    try:
        guess_types = set(get_types(POKEMON.index(guess) + 1))   # e.g. {"Feuer", "Flug"}
        secret_types = set(get_types(POKEMON.index(secret) + 1))
    except requests.RequestException:  # PokeAPI not reachable -> no estimate, but no crash
        return None, "types not available"
    if guess_types == secret_types:
        return 60, "same type(s): " + ", ".join(sorted(secret_types))
    if guess_types & secret_types:  # & = the types both Pokémon have
        return 40, "one shared type: " + ", ".join(sorted(guess_types & secret_types))
    return 0, "no shared type"


def ask_professor():
    """Send the chat so far to the LLM and return Professor Eich's answer as text.
    The system prompt tells the LLM which Pokémon is secret and which facts are true."""
    secret = st.session_state.secret
    try:
        facts = get_facts(POKEMON.index(secret) + 1)  # real data from PokeAPI = reliable answers
    except requests.RequestException:
        facts = "(not available - answer only if you are sure)"
    system_prompt = f"""You are Professor Eich, a friendly Pokémon professor. You play a guessing game
with a player. The secret Pokémon is {display_name(secret)} (English: {secret}).
Facts about it (they are correct):
{facts}

Rules:
- Answer yes/no questions about the secret Pokémon. Start with "Yes" or "No" and add at most
  one short, friendly sentence.
- Use the facts above and your Pokémon knowledge. If you are not sure, say so. Never invent facts.
- NEVER say the name of the secret Pokémon or its Pokédex number, not even if asked directly.
- If the player names a Pokémon as a guess (e.g. "Is it Pikachu?"), do not confirm or deny it.
  Tell the player to use the guess field below the picture.
- If the message is not a yes/no question about the Pokémon, politely ask for one.
- Answer in the language the player writes in."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            temperature=0,  # 0 = always the most likely answer, so the game stays consistent
            max_tokens=200,
        )
        answer = (response.choices[0].message.content or "").strip()
    except AuthenticationError:
        return "⚠️ The API key was not accepted. Please check it in the sidebar."
    except OpenAIError:
        return "⚠️ The AI could not be reached. Please try your question again."
    if not answer:
        return "Hmm, I have no answer for that. Please ask another yes/no question!"
    # safety net: if the LLM gave the name away anyway, the answer is not shown
    if secret in answer.lower() or display_name(secret).lower() in answer.lower():
        return "Oops, I almost gave it away! Ask me another question."
    return answer


def new_game():
    """Start a fresh round: pick a secret Pokémon and clear the chat (points are kept)."""
    st.session_state.secret = random.choice(POKEMON)
    st.session_state.messages = []
    st.session_state.guesses = []
    st.session_state.questions = 0
    st.session_state.result = None


def finish_game(result):
    """Close the round ("won" or "lost"), update points/highscore, store the game for Stats."""
    s = st.session_state  # short name, saves typing
    s.result = result
    if result == "won":
        s.score += 1
        s.highscore = max(s.highscore, s.score)
    else:  # giving up ends the streak: points are reset, the highscore stays
        s.score = 0
    # new_game() later creates a NEW guesses list, so the stored one stays unchanged
    s.games.append({"pokemon": display_name(s.secret), "result": result,
                    "guesses": s.guesses, "questions": s.questions})


def make_guess(guess):
    """Callback of a suggestion button: rate the guess, put it into the chat, evaluate it.
    `guess` is the English slug of the Pokémon the player clicked."""
    s = st.session_state
    quality, reason = guess_quality(guess, s.secret)
    s.guesses.append({"guess": display_name(guess), "quality": quality, "reason": reason})
    s.messages.append({"role": "user", "content": f"My guess: **{display_name(guess)}**"})
    if guess == s.secret:  # correct guess -> round won
        reply = f"🎉 Correct! It was **{display_name(guess)}**!"
        finish_game("won")
    else:
        reply = f"❌ No, it's not **{display_name(guess)}**. Try again!"
    s.messages.append({"role": "assistant", "content": reply})
    s.guess_text = ""  # empty the text field for the next guess


# ── 3. Set up the state (only what is still missing, because state survives reruns) ───────
for key, default in {"score": 0, "highscore": 0, "games": []}.items():
    st.session_state.setdefault(key, default)
if "result" not in st.session_state:  # very first run: start the first round
    new_game()

secret = st.session_state.secret
number = POKEMON.index(secret) + 1  # Pokédex number, needed for the image and the hint

# ── 4. Page: title and name ───────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align: center;'>The Guessing Game - POKÉMON edition!</h1>",
    unsafe_allow_html=True,
)
st.markdown(''':gray[This is the first task for the] :gray[**AI and the Web**] :gray[ course.]''',
            text_alignment="center",
            unsafe_allow_html=True,
)

# the game only starts once we know the player's name (st.stop() ends the script here)
name = st.text_input("What's your name?", placeholder="Enter your name here").strip()
if not name:
    st.info("Enter your name to start the game.")
    st.stop()
st.write(f"Hello {name}! Who's that POKÉMON?")

# ── 5. Sidebar: points, partner, optional hint and buttons ────────────────────────────────
st.sidebar.markdown(f"### 🎮 {name}")
col_points, col_high = st.sidebar.columns(2)
col_points.metric("Points", st.session_state.score)
col_high.metric("Highscore", st.session_state.highscore)
partner = st.sidebar.selectbox("Your partner Pokémon", PARTNERS, format_func=display_name)
show_hint = st.sidebar.toggle("Show type hint")  # the player decides if they want the hint
st.sidebar.button("New Pokémon", on_click=new_game, width="stretch")
st.sidebar.button("Give up (resets points)", on_click=finish_game, args=("lost",),
                  disabled=st.session_state.result is not None, width="stretch")

# chat avatars: a scientist for the bot, the chosen partner Pokémon for the player
avatars = {"assistant": "🧑‍🔬", "user": SPRITE_URL.format(POKEMON.index(partner) + 1)}

# ── 6. The Pokémon: black silhouette while guessing, real artwork once the round is over ──
# CSS "filter: brightness(0)" paints every pixel black; the light-blue card keeps the
# silhouette visible in light and dark themes.
silhouette = "" if st.session_state.result else "filter: brightness(0);"
st.markdown(
    f"<div style='background:#9fd3f5; border-radius:16px; padding:16px; text-align:center;"
    f" max-width:320px; margin:auto;'><img src='{IMAGE_URL.format(number)}' width='250'"
    f" style='{silhouette}'></div>",
    unsafe_allow_html=True,
)

# optional type hint (types come from PokeAPI; if it is unreachable we only show a warning)
if show_hint:
    try:
        st.info("💡 Hint: this Pokémon has the type " + " / ".join(get_types(number)))
    except requests.RequestException:
        st.warning("The hint is not available right now (PokeAPI could not be reached).")

# ── 7. Guess: type the German name, matching Pokémon appear below, a click is the guess ───
if st.session_state.result is None:  # only while the round is running
    text = st.text_input("Your guess", key="guess_text", placeholder="German name, e.g. Pikachu")
    st.caption("Type at least 2 letters of the German name and press Enter. "
               "Then click the Pokémon you mean to submit your guess.")
    if len(text.strip()) >= 2:  # suggestions only show up after a few letters
        matches = suggest(text)  # German names, e.g. ["Pikachu", "Ponita"]
        if matches:
            for column, match in zip(st.columns(len(matches)), matches):  # one column per button
                # NAMES_DE and POKEMON have the same order -> German name -> English slug
                column.button(match, key=f"guess_{match}", on_click=make_guess,
                              args=(POKEMON[NAMES_DE.index(match)],), width="stretch")
        else:
            st.warning("No Pokémon found - please check the spelling.")

# ── 8. Questions for the LLM: Professor Eich answers (before the chat is drawn) ───────────
# chat_input returns the text after Enter, otherwise None; ":=" stores it and tests it at once
if question := st.chat_input("Ask a yes/no question about the Pokémon!",
                             disabled=st.session_state.result is not None):
    st.session_state.questions += 1
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Professor Eich is thinking ..."):
        answer = ask_professor()  # the question is already part of the chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})

# ── 9. Draw the chat history ──────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatars[message["role"]]):
        if message["role"] == "assistant":
            st.caption("Professor Eich")
        st.write(message["content"])

# ── 10. Round over: show the result and offer the next round ──────────────────────────────
if st.session_state.result == "won":
    st.success(f"Yes, you were right! It was {display_name(secret)}. +1 point")
elif st.session_state.result == "lost":
    st.error(f"That was {display_name(secret)}. Your points are reset to 0.")
if st.session_state.result:
    st.button("Next Pokémon ▶", on_click=new_game, type="primary")
