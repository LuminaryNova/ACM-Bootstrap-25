import google.generativeai as genai
import streamlit as st
from tavily import TavilyClient
import json
import PyPDF2
import os

LATEX_INSTRUCTION = """
- For all mathematical expressions, equations, integrals, and fractions, format them using LaTeX syntax.
- For example, instead of 'x^2 / 2', write `$\\frac{x^2}{2}$`. Instead of 'integral of x from 0 to 1', write `$\\int_0^1 x dx$`.
- Always wrap inline math with single dollar signs (`$ ... $`).
- Always wrap block math (equations on their own line) with double dollar signs (`$$ ... $$`).
"""

try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
except KeyError:
    st.error("🚨 Please set GEMINI_API_KEY and TAVILY_API_KEY as environment variables.")
    st.stop()

SYSTEM_INSTRUCTION_CHAT = f"You are a helpful AI tutor. {LATEX_INSTRUCTION}"
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION_CHAT)
generation_model = genai.GenerativeModel('gemini-1.5-flash')

def is_study_related(prompt:str) -> bool:
    check_prompt = f"""
    You are a strict filter for an AI tutoring app.
    Decide if the following prompt is related to academic study (math, science, engineering, history, literature, exam prep, etc..).
    Prompt: "{prompt}"
    Answer with only "YES" if it is study-related, or 'NO' if it is not.
    """
    try:
        response = generation_model.generate_content(check_prompt)
        answer = response.text.strip().upper()
        return answer.startswith("Y")
    except Exception as e:
        st.error(f"Error during content filtering: {e}")
        return False

def gemini(prompt):
    if not is_study_related(prompt):
        st.warning("⚠️ This app only supports study-related questions. Please ask something academic.")
        return None
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        yield chunk.text

def generate_single_response(prompt):
    response = generation_model.generate_content(prompt)
    return response.text

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

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
            with st.spinner("AI is thinking..."):
                response_generator = gemini(prompt)
                if response_generator:
                    full_response = st.write_stream(response_generator)
                    st.session_state.chat_history.append(("assistant", full_response))

elif page == "Topic Questions":
    st.title("Topic Questions")
    with st.form("topic_form"):
        st.write("Select your options to generate practice questions.")
        topic = st.text_input("Topic", placeholder="e.g., Integrals, Newton's Laws")
        question_type = st.radio("Type of Questions", ["Multiple Choice", "Numerical", "Subjective"])
        num_questions = st.slider("Number of Questions", 1, 10, 3)
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
                tavily = TavilyClient(api_key=TAVILY_API_KEY)
                search_query = f"in depth {question_type} questions and answers for a quiz on {topic} at a {difficulty} level"
                search_results = tavily.search(query=search_query, search_depth='advanced', max_results=5)
                context = "\n".join([result.get("content", "") for result in search_results.get("results", [])])

                if question_type == "Multiple Choice":
                    json_format_instruction = 'Each object must have three keys: "question", "options" (list of 4 strings), and "answer" (the correct option).'
                else:
                    json_format_instruction = 'Each object must have two keys: "question" and "answer".'
                prompt_for_questions = f"""
Based ONLY on the following context, generate exactly {num_questions} questions of the type '{question_type}' on the topic "{topic}".
Context from the web search:

Here are your formatting rules:
{LATEX_INSTRUCTION}

---
{context}
---

Format the entire output as a single, valid JSON list of objects. Do not include any text, titles, or explanations before or after the JSON list.
{json_format_instruction}
"""
                response_text = generate_single_response(prompt_for_questions)
                if response_text:
                    clean_response = response_text.strip().replace("```json", "").replace("```", "")
                    st.session_state.generated_questions = json.loads(clean_response)
                else:
                    st.session_state.generated_questions = None
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.generated_questions = None

    if st.session_state.generated_questions:
        st.subheader(f"Here are your {question_type} questions on {topic}:")
        for i, qa in enumerate(st.session_state.generated_questions):
            st.markdown(f"**Question {i + 1}:** \n{qa.get('question', 'N/A')}")
            if question_type == "Multiple Choice" and "options" in qa:
                for opt in qa["options"]:
                    st.markdown(f"- {opt}")
            if st.button(f"Show Answer", key=f"q_{i}"):
                st.session_state.answer_visibility[i] = not st.session_state.answer_visibility.get(i, False)
            if st.session_state.answer_visibility.get(i, False):
                st.success(f"**Answer:** {qa.get('answer', 'N/A')}")
            st.divider()

elif page == "Revision Notes":
    st.title("Revision Notes")
    if "revision_notes" not in st.session_state:
        st.session_state.revision_notes = ""
    tab1, tab2 = st.tabs(["Generate from topic", "Summarize my Text/Document"])

    with tab1:
        st.subheader("Generate Notes from Topic")
        with st.form("notes_from_topic_form"):
            topic = st.text_input("Topic", placeholder="e.g. Pythagoras Theorem, Shifting of Curves")
            submitted_topic = st.form_submit_button("Generate Notes")

        if submitted_topic and topic:
            with st.spinner(f"Generating revision notes on {topic}..."):
                try:
                    tavily = TavilyClient(api_key=TAVILY_API_KEY)
                    search_query = f"in-depth explanation and key points about the topic: {topic}"
                    search_results = tavily.search(query=search_query, search_depth='advanced', max_results=5)
                    context = "\n".join([result["content"] for result in search_results["results"]])

                    prompt_for_notes = f"""
                    Based on the following context from a web search, generate a comprehensive set of revision notes on the topic "{topic}".
                    The notes should be well-structured, easy to understand, and cover the key points.
                    Use markdown formatting, including headings, subheadings, bullet points, and bold text for important terms.
                    
                    Here are your formatting rules for math:
                    {LATEX_INSTRUCTION}

                    Context:
                    ---
                    {context}
                    ---
                    """
                    notes = generate_single_response(prompt_for_notes)
                    if notes:
                        st.session_state.revision_notes = notes
                except Exception as e:
                    st.error(f"An error occurred while generating notes: {e}")

    with tab2:
        st.subheader("Summarize my Text/Document")
        pasted_text = st.text_area("Paste your text here to summarize", height=250)
        uploaded_file = st.file_uploader("Or upload a document(.txt, .pdf)", type=["txt", "pdf"])
        if st.button("Generate Summary"):
            input_text = ""
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    input_text = extract_text_from_pdf(uploaded_file)
                else:
                    input_text = uploaded_file.read().decode("utf-8")
            elif pasted_text:
                input_text = pasted_text

            if input_text:
                with st.spinner("Generating summary..."):
                    prompt_for_summary = f"""
                    Create a concise set of revision notes from the following text.
                    The notes should be well-structured, easy to understand, and capture the key points and concepts.
                    Use markdown formatting, including headings, subheadings, bullet points, and bold text for important terms.

                    Here are your formatting rules for math:
                    {LATEX_INSTRUCTION}

                    Text to Summarize:
                    ---
                    {input_text}
                    ---
                    """
                    notes = generate_single_response(prompt_for_summary)
                    if notes:
                        st.session_state.revision_notes = notes
            else:
                st.warning("Please paste text or upload a document to summarize.")

    if st.session_state.revision_notes:
        st.divider()
        st.subheader("Your Generated Revision Notes")
        st.markdown(st.session_state.revision_notes)