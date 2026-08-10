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
        api_key = os.getenv("GEMINI_API_KEY")
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.5-flash")

        prompt = (
            "Summarize the following news article in 2-3 clear sentences. "
            "No fluff, just the key facts.\n\n"
            f"{article_text}"
        )

        response = model.generate_content(prompt)
        return response.text.strip()
