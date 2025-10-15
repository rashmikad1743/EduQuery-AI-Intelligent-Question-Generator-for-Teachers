import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def generate_with_gemini(text):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are an expert teacher.
    Based on the following content, generate 5 academic questions 
    (mix of MCQ, short answer, and descriptive).

    Context:
    {text}

    Format:
    1. ...
    2. ...
    3. ...
    """

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        questions = [q.strip() for q in result.split('\n') if q.strip()]
        return questions
    except Exception as e:
        return [f"Error: {str(e)}"]
