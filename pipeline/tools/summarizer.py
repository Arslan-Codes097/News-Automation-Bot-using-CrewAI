import os
import time
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SummarizerInput(BaseModel):
    article_text: str = Field(description="Raw article title, snippet, and source to summarize")


class SummarizerTool(BaseTool):
    name: str = "summarizer"
    description: str = "Summarizes a news article into a short, clear 2-3 sentence update"
    args_schema: type[BaseModel] = SummarizerInput

    def _run(self, article_text: str) -> str:
        # Sleep for 15 seconds to respect Gemini API free tier rate limit
        time.sleep(15)
        
        api_key = os.getenv("GEMINI_API_KEY")
        import litellm

        prompt = (
            "Summarize the following news article in 2-3 clear sentences. "
            "No fluff, just the key facts.\n\n"
            f"{article_text}"
        )

        response = litellm.completion(
            model="gemini/gemini-flash-latest",
            api_key=api_key,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
