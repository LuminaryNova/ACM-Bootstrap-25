def analyze_question(question, llm_client):
    prompt = f"""
    You are an educational topic analyzer.  
    Break the question down into:
    1. Broad field of study (choose from: Math, Physics, Chemistry, Biology, Computer Science, General Knowledge).
    2. Sub-topic(s): 1-3 short, specific tags relevant to the question.  
    Example:
    Q: "What is Newton's second law?"
    → Field: Physics
    → Sub-topics: ["Mechanics", "Forces", "Laws of Motion"]

    Q: "Solve x + y = 10 and x - y = 2"
    → Field: Math
    → Sub-topics: ["Algebra", "Linear Equations", "Two Variables"]

    Now analyze:
    Q: "{question}"
    """
    response = llm_client(prompt)
    return response
