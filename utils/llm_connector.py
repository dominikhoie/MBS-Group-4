import httpx
import asyncio
import os

from features.qa_system.qa_data import QA_DATABASE

API_URL = "http://134.60.124.44:8000"
API_KEY = os.getenv("LLM_API_KEY")
USER_ID = "group4"

def build_system_prompt(language: str = "en") -> str:
    if language == "de":
        prompt_lines = [
            "Du bist ein hilfreicher Assistent für den Bamboolino Indoor-Spielplatz.",
            "Beantworte Benutzerfragen ausschließlich basierend auf den folgenden Fakten.",
            "Wenn du etwas nicht weißt, sag einfach, dass du es nicht weißt.\n"
        ]
    else:
        prompt_lines = [
            "You are a helpful assistant for the Bamboolino indoor playground.",
            "Answer user questions only using the following facts.",
            "If you don't know something, just say you don't know.\n"
        ]
    
    for key, data in QA_DATABASE.items():
        if language in data:
            section_title = key.replace("_", " ").title()
            prompt_lines.append(f"{section_title}:\n{data[language]}")
    
    return "\n\n".join(prompt_lines)

async def query_llm(user_input: str, language: str = "en", max_tokens: int = 64) -> str:
    history = [
        {
            "role": "system",
            "content": [{"type": "text", "text": build_system_prompt(language)}]
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": user_input}]
        }
    ]

    payload = {
        "user_id": USER_ID,
        "messages": history,
        "max_new_tokens": max_tokens
    }

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_URL}/tasks", json=payload, headers=headers)
            resp.raise_for_status()
            task_id = resp.json()["task_id"]
        except Exception as e:
            return f"❌ Fehler beim Senden: {e}"

        while True:
            try:
                result = await client.get(f"{API_URL}/tasks/{task_id}/response")
                result.raise_for_status()
                data = result.json()
                messages = data.get("response")

                if messages:
                    return messages[-1]["content"][0]["text"]
                await asyncio.sleep(2)
            except Exception as e:
                return f"❌ Fehler beim Empfangen: {e}"