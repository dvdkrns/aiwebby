# ══ STATS PAGE: numbers and charts about the finished games ═══════════════════════════════
import pandas as pd  # DataFrame = table that st.bar_chart can draw
import streamlit as st

st.header("Stats")

# finished games are collected by the Play page (see finish_game there); .get() returns []
# if nobody has opened the Play page yet, so this page can never crash
games = st.session_state.get("games", [])
if not games:
    st.info("No finished games yet. Play a round on the Play page first!")
    st.stop()

# one row per finished game; the quality of a game is the average quality of its guesses
rows = []
for number, game in enumerate(games, start=1):
    qualities = [g["quality"] for g in game["guesses"] if g["quality"] is not None]
    rows.append({
        "Game": number,
        "Pokémon": game["pokemon"],
        "Result": game["result"],
        "Guesses": len(game["guesses"]),
        "Quality": sum(qualities) / len(qualities) if qualities else None,
    })
df = pd.DataFrame(rows)  # list of dicts -> table, one column per key

# ── Key numbers ───────────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)  # four boxes side by side
col1.metric("Games played", len(df))
col2.metric("Games won", int((df["Result"] == "won").sum()))
col3.metric("Ø guesses per game", f"{df['Guesses'].mean():.1f}")
col4.metric("Highscore", st.session_state.get("highscore", 0))

st.caption(f"Professor Eich answered {sum(g['questions'] for g in games)} questions in total.")

# ── Guesses per game ──────────────────────────────────────────────────────────────────────
st.subheader("Guesses per game")
st.bar_chart(df, x="Game", y="Guesses")  # one bar per game

# ── Guess quality ─────────────────────────────────────────────────────────────────────────
st.subheader("Guess quality")
if df["Quality"].notna().any():  # at least one game has a quality value
    st.metric("Ø quality of all guesses", f"{df['Quality'].mean():.0f} / 100")
    st.bar_chart(df, x="Game", y="Quality")
else:
    st.warning("No quality values yet (the type data from PokeAPI could not be loaded).")

with st.expander("How is the quality estimated?"):
    st.markdown("""
Every guess is compared with the secret Pokémon by its **types** (taken from PokeAPI):

| Guess | Quality |
|---|---|
| The right Pokémon | 100 |
| Another Pokémon with exactly the same type(s) | 60 |
| Another Pokémon that shares one type | 40 |
| A Pokémon that shares no type | 0 |

The quality of a game is the average of its guesses. This is only a rough estimate:
two Pokémon can share a type and still look nothing alike.
""")

# ── Every single guess, so the estimate can be checked ────────────────────────────────────
st.subheader("All guesses")
log = [{"Game": number, "Secret": game["pokemon"], "Guess": g["guess"],
        "Quality": g["quality"], "Why": g["reason"]}
       for number, game in enumerate(games, start=1) for g in game["guesses"]]
if log:
    st.dataframe(pd.DataFrame(log), hide_index=True)
else:
    st.caption("No guesses yet - in these games you gave up right away.")
