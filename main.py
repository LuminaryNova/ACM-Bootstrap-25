from analyze import analyze_question
from google import genai
import dspy
import streamlit as st  

genai.configure(api_key="AIzaSyB3tmEYVAvY8jjD4pRqPy0euD1-VIpCQGo")
model = genai.GenerativeModel('gemini-1.5-flash')

def gemini(prompt):
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        yield chunk.text

st.set_page_config(page_title="AI Tutor", page_icon="🤖", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Q&A Chat", "Topic Questions", "Revision Notes"])

if page == "Q&A Chat":
    st.title("AI Tutor - Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for sender, msg in st.session_state.chat_history:
        with st.chat_message(sender):
            st.markdown(msg)

    if prompt := st.chat_input("Type your question here..."):
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_generator = gemini(prompt)
            full_response = st.write_stream(response_generator)
        
        st.session_state.chat_history.append(("assistant", full_response))

elif page == "Topic Questions":
    st.title("Topic Questions")
    st.write("Here you'll get questions from the internet based on your topics (to be implemented).")

elif page == "Revision Notes":
    st.title("Revision Notes")
    st.write("Here you'll get revision notes (to be implemented).")
