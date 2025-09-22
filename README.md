# AI Tutor - ACM Bootstrapper 2025

AI Tutor is an interactive tutoring web app built with Streamlit, using **Google Gemini AI** and a **custom Tavily integration (RAG implementation)** developed by CodeShot to generate:

- Q&A Chat with study-related prompts
- Topic-specific practice questions
- Revision notes from topics or uploaded text/documents

---

## Features

1. **Q&A Chat**  
   - Ask academic questions (math, science, literature, history, etc.)  
   - AI responds with explanations and solutions  
   - Supports LaTeX formatting for mathematical expressions, integrals, and fractions

2. **Topic Questions (RAG Implementation)**  
   - Generate multiple choice, numerical, or subjective questions  
   - Difficulty levels: Easy, Medium, Hard  
   - Uses **Retrieval-Augmented Generation (RAG)**: the app fetches relevant web content via **Tavily API** and feeds it to the AI model to generate context-aware questions  
   - Tavily integration developed by the author

3. **Revision Notes (RAG Implementation)**  
   - Generate notes from a topic or uploaded text/PDF  
   - Structured with headings, bullet points, and formatted math  
   - Uses RAG to retrieve relevant context before generating notes

4. **Content Filtering**  
   - Only allows study-related prompts  
   - Warns users if the input is non-academic

---

## Installation / Local Setup

1. Clone the repository:

```bash
git clone https://github.com/LuminaryNova/ACM-Bootstrap-25.git
cd ACM-Bootstrap-25

