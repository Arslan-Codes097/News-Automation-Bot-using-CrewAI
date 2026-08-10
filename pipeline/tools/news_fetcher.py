import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class NewsFetcherInput(BaseModel):
    query: str = Field(description="Search query for news")


class NewsFetcherTool(BaseTool):
    name: str = "news_fetcher"
    description: str = "Fetches the latest news headlines and links for a given search query"
    args_schema: type[BaseModel] = NewsFetcherInput

    def _run(self, query: str) -> str:
        api_key = os.getenv("SERPER_API_KEY")
        url = "https://google.serper.dev/news"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {"q": query, "num": 3}

        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        articles = data.get("news", [])
        if not articles:
            return "No articles found."

        formatted = []
        for article in articles:
            title = article.get("title", "")
            link = article.get("link", "")
            snippet = article.get("snippet", "")
            source = article.get("source", "")
            formatted.append(f"Title: {title}\nSource: {source}\nLink: {link}\nSnippet: {snippet}\n")

        return "\n---\n".join(formatted)
