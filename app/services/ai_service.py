import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_text(text: str):

    prompt = f"""
Ты анализируешь обращения клиентов банка.

Верни строго JSON без пояснений и без markdown.

Формат:

{{
  "issue_type": "Жалоба | Смена данных | Консультация | Претензия | Неработоспособность приложения | Мошеннические действия | Спам",
  "sentiment": "Позитивный | Нейтральный | Негативный",
  "priority_score": число от 1 до 10,
  "language": "RU | KZ | ENG",
  "summary": "Краткое описание (1-2 предложения)",
  "recommendation": "Рекомендация менеджеру"
}}

Текст обращения:
{text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        raw_text = response.text.strip()

        print("RAW RESPONSE:", raw_text)

        # Если модель вернула ```json ```
        if "```" in raw_text:
            parts = raw_text.split("```")
            if len(parts) >= 2:
                raw_text = parts[1]

        # Берём только JSON внутри текста
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1

        if start != -1 and end != -1:
            raw_text = raw_text[start:end]

        result = json.loads(raw_text)

        return result

    except Exception as e:
        print("Ошибка Gemini:", e)
        return {
            "issue_type": "Не определено",
            "sentiment": "Нейтральный",
            "priority_score": 5,
            "language": "RU",
            "summary": "Ошибка анализа",
            "recommendation": "Проверить вручную"
        }