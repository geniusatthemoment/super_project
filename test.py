import requests
from config import API_AI

URL = "https://api.intelligence.io.solutions/api/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_AI}"
}

def get_ai_response(user_text: str) -> str:
    try:
        payload = {
            "model": "deepseek-ai/DeepSeek-R1-0528",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text},
            ],
        }
        resp = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        if "</think>" in content:
            content = content.split("</think>", 1)[1].lstrip("\n")

        return content.strip() or "Пустой ответ от AI."
    except Exception as e:
        return f"Ошибка при обращении к AI: {e}"