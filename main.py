from analyze import analyze_question
from google import genai
import dspy
import streamlit as st  

client = genai.Client(api_key="AIzaSyDvyGaKRxXsjUNT7RugtIlrOeYlGhscdoM")

def gemini(prompt):
    response = client.models.generate_content(model="gemini-2.5-flash",contents=prompt)
    return response.text

test_question = "What is 2 + 2?"
print(analyze_question(test_question, gemini))