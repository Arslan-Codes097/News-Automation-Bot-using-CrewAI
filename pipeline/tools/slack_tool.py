import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SlackToolInput(BaseModel):
    headline: str = Field(description="Article headline")
    summary: str = Field(description="Short summary of the article")
    link: str = Field(description="Source URL of the article")


class SlackTool(BaseTool):
    name: str = "slack_poster"
    description: str = "Posts a formatted football news update to Slack"
    args_schema: type[BaseModel] = SlackToolInput

    def _run(self, headline: str, summary: str, link: str) -> str:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        if link.lower() in ["n/a", "none", "", "null"]:
            text = f"*{headline}*\n{summary}"
        else:
            if not link.startswith("http"):
                link = "https://" + link
            text = f"*{headline}*\n{summary}\n<{link}|Read more>"

        message = {
            "text": text
        }

        response = requests.post(webhook_url, json=message, timeout=15)
        response.raise_for_status()

        return f"Posted to Slack: {headline}"
