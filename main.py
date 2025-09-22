import google.generativeai as genai
import streamlit as st  
import os
from tavily import TavilyClient
import json

genai.configure(api_key=st.secrets["api_keys"]["gemini_api_key"])
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def gemini(prompt):
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        yield chunk.text
def generate_questions(prompt):
    response = model.generate_content(prompt)
    return response.text    

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
    with st.form("topic_form"):
        st.write("Select your options to generate practice questions.")
        topic = st.text_input("Topic" , placeholder = "e.g., Algebra, Newton's Laws")
        question_type = st.radio("Type of Questions",["Multiple Choice","Numerical","Subjective"])
        num_questions = st.slider("Number of Questions", 1,10, 1)
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
        submitted = st.form_submit_button("Generate Questions")

    if "generated_questions" not in st.session_state:
        st.session_state.generated_questions = None
    
    if "answer_visibility" not in st.session_state:
        st.session_state.answer_visibility = {} 
    
    if submitted:
        st.session_state.answer_visibility = {}
        with st.spinner(f"Searching the web and generating {num_questions} {question_type} questions on {topic}..."):
            try:
                tavily = TavilyClient(api_key=st.secrets["api_keys"]["tavily_api_key"])
                search_query = f"in depth {question_type} questions and answers for a quiz on {topic} at a {difficulty} level"
                search_results = tavily.search(query = search_query,search_depth = 'advanced', max_results=5)
                context = "\n".join([result["content"] for result in search_results["results"]])
            except (KeyError, AttributeError):
                st.error("Error fetching data from Tavily. Please check your API key and internet connection.")
                st.stop()
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.stop()
            
            if question_type == "Multiple Choice":
                json_format_instruction = """
                Each object must have three keys: "question", "options"(a list of 4 strings), and "answer"(the correct option string)."""
            else:
                json_format_instruction = """
                Each object must have two keys: "question" and "answer" """
            prompt_for_questions = f""" Based ONLY on the following context, generate exactly {num_questions} questions of the type '{question_type}' on the topic "{topic}".
                                        Context from the web search:
                                        ---
                                        {context}
                                        ---
                                        Format the entire output as a single, valid JSON list of objects. Do not include any text, titles, or explanations before or after the JSON list.
                                        {json_format_instruction}
                                        """    
            response_text = generate_questions(prompt_for_questions)
            try:
                clean_response = response_text.strip().replace("```json", "").replace("```", "")
                st.session_state.generated_questions = json.loads(clean_response)
            except (json.JSONDecodeError, TypeError):
                st.error("Failed to parse the generated questions. Please try again.")
                st.session_state.generated_questions = None

            if st.session_state.generated_questions:
                st.subheader(f"Here are your {question_type} questions on {topic}:")
                for i, qa in enumerate(st.session_state.generated_questions):
                    st.markdown(f"**Question {i + 1}:** {qa.get('question', 'N/A')}")
            
                    if question_type == "MCQ" and "options" in qa:
                        for opt in qa["options"]:
                            st.markdown(f"- {opt}")
            
                    if st.button(f"Show Answer", key=f"q_{i}"):
                        st.session_state.answer_visibility[i] = not st.session_state.answer_visibility.get(i, False)

                    if st.session_state.answer_visibility.get(i, False):
                        st.success(f"**Answer:** {qa.get('answer', 'N/A')}")
            
                    st.divider()

                
                
        
elif page == "Revision Notes":
    st.title("Revision Notes")
    st.write("Here you'll get revision notes (to be implemented).")