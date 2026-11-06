# streamlit run task1-template/app.py
import streamlit as st

# i wanted to center the title and caption which is not possiblie in Streamlit
# i used markdown instead and looked up how to center it
st.markdown(
    "<h1 style='text-align: center;'>The Guessing Game for Fame</h1>",
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
st.write("Hello, ", name, "! Are you ready to play?")

st.button("Reset", type="primary")
if st.button("Say hello"):
    st.write("Why hello there")
else:
    st.write("Goodbye")

if st.button("Aloha", type="tertiary"):
    st.write("Ciao")