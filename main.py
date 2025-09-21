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


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if page == "Q&A Chat":
    st.title("AI Tutor - Chat")

    chat_container = st.container()
    with chat_container:
        for sender, msg in st.session_state.chat_history:
            if sender == "user":
                st.markdown(f"<div style='background-color:#000000;color:#FFFFFF;padding:10px;border-radius:10px;margin:5px 0;text-align:right'><b>You:</b>{msg}</div>",unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color:#000000;color:#FFFFFF;padding:10px;border-radius:10px;margin:5px 0;text-align:left'><b>AI:</b>{msg}</div>",unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .chat-box {
            position: fixed;
            bottom: 0;
            left: 18rem;
            right: 1rem;
            background: black;
            padding: 10px;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .chat-box input {
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border-radius: 12px;
            border: 1px solid #ccc;
            color: #000000;
        }
        .send-btn {
            padding: 12px 18px;
            font-size: 16px;
            border-radius: 12px;
            border: none;
            background-color: #4CAF50;
            color: w;
            cursor: pointer;
        }
        .send-btn:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    with st.container():
        cols = st.columns([6, 1])
        with cols[0]:
            user_input = st.text_input(
                "", value="", placeholder="Type your question here...",
                key="input_box", label_visibility="collapsed"
            )
        with cols[1]:
            send = st.button("➤", key="send_button")


    if send and user_input.strip():
        
        st.session_state.chat_history.append(("user", user_input))
        ai_response = gemini(user_input)
        st.session_state.chat_history.append(("ai", ai_response))
        st.rerun()


elif page == "Topic Questions":
    st.title("Topic Questions")
    st.write("Here you'll get questions from the internet based on your topics (to be implemented).")

elif page == "Revision Notes":
    st.title("Revision Notes")
    st.write("Here you'll get revision notes (to be implemented).")