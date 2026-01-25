import os
import openai
import httpx

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def query_ai(prompt: str):
    # Primero OpenAI
    if OPENAI_KEY:
        openai.api_key = OPENAI_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    # Si falla, Gemini
    if GEMINI_KEY:
        headers = {"Authorization": f"Bearer {GEMINI_KEY}"}
        r = httpx.post("https://api.generative.google/v1beta2/models/text-bison-001:generate",
                       headers=headers, json={"prompt": prompt})
        return r.json().get("candidates", [{}])[0].get("content", "No response")

    return "AI unavailable"
