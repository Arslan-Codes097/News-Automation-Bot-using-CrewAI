import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SummarizerInput(BaseModel):
    article_text: str = Field(description="Raw article title, snippet, and source to summarize")


class SummarizerTool(BaseTool):
    name: str = "summarizer"
    description: str = "Summarizes a news article into a short, clear 2-3 sentence update"
    args_schema: type[BaseModel] = SummarizerInput

    def _run(self, article_text: str) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt = (
            "Summarize the following news article in 2-3 clear sentences. "
            "No fluff, just the key facts.\n\n"
            f"{article_text}"
        )

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 200
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"].strip()
