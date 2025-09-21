from analyze import analyze_question
from google import genai
import dspy
import streamlit as st  

client = genai.Client(api_key="AIzaSyB3tmEYVAvY8jjD4pRqPy0euD1-VIpCQGo")

def gemini(prompt):
    response = client.models.generate_content(model="gemini-2.5-flash-lite",contents=prompt)
    return response.text

st.set_page_config(page_title="AI Tutor", page_icon="🤖", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Q&A Chat", "Topic Questions", "Revision Notes"])

if page == "Q&A Chat":
    st.title("AI Tutor - Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for sender, msg in st.session_state.chat_history:
        role = "user" if sender == "user" else "assistant"
        with st.chat_message("user"):
            st.markdown(prompt)

    if prompt := st.chat_input("Type your question here..."):
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        ai_response = gemini(prompt)
        st.session_state.chat_history.append(("ai", ai_response))
        with st.chat_message("assistant"):
            st.markdown(ai_response)

elif page == "Topic Questions":
    st.title("Topic Questions")
    st.write("Here you'll get questions from the internet based on your topics (to be implemented).")

elif page == "Revision Notes":
    st.title("Revision Notes")
    st.write("Here you'll get revision notes (to be implemented).")
