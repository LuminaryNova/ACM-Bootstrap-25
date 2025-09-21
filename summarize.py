def summarize(text, llm_client):
    prompt = f"You are now a summarizer. Summarize the following question answer pair in a couple sentences: {text}"
    