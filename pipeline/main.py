import os
from dotenv import load_dotenv
load_dotenv()
from crewai import Agent, Task, Crew, Process, LLM
from tools.news_fetcher import NewsFetcherTool
from tools.summarizer import SummarizerTool
from tools.slack_tool import SlackTool
from tools.sheets_logger import SheetsLoggerTool


def build_crew():
    llm_researcher = LLM(model="groq/llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    llm_summarizer = LLM(model="groq/llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    llm_publisher = LLM(model="groq/llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

    news_fetcher_tool = NewsFetcherTool()
    summarizer_tool = SummarizerTool()
    slack_tool = SlackTool()
    sheets_tool = SheetsLoggerTool()

    researcher = Agent(
        role="{topic} News Researcher",
        goal="Find the latest and most relevant {topic} news",
        backstory="An experienced journalist who tracks news and trends about {topic}.",
        tools=[news_fetcher_tool],
        llm=llm_researcher,
        verbose=True
    )

    summarizer = Agent(
        role="{topic} News Summarizer",
        goal="Turn raw {topic} articles into short, clear summaries",
        backstory="A sharp editor who condenses stories into quick, readable updates without losing key facts.",
        tools=[summarizer_tool],
        llm=llm_summarizer,
        verbose=True
    )

    publisher = Agent(
        role="News Publisher",
        goal="Distribute summarized {topic} news to Slack and log it to Google Sheets",
        backstory="A newsroom assistant responsible for getting finished updates out to the team and keeping records.",
        tools=[slack_tool, sheets_tool],
        llm=llm_publisher,
        verbose=True
    )

    fetch_task = Task(
        description="Search for the latest news using the query '{topic} news today'. Return the raw list of articles with titles, links, and snippets.",
        expected_output="A list of {topic} news articles with title, source, link, and snippet for each.",
        agent=researcher
    )

    summarize_task = Task(
        description="Take the fetched articles and summarize each one into a short, clear 2-3 sentence update. Remove duplicate stories covering the same event.",
        expected_output="A list of summarized {topic} updates, each with headline, summary, and source link.",
        agent=summarizer,
        context=[fetch_task]
    )

    publish_task = Task(
        description="For each summarized update, post it to Slack and log it as a new row in Google Sheets. ONLY process actual news articles. Ignore any conversational text or introductory sentences like 'Here are the unique articles'.",
        expected_output="Confirmation that all updates were posted to Slack and logged to Sheets.",
        agent=publisher,
        context=[summarize_task]
    )

    crew = Crew(
        agents=[researcher, summarizer, publisher],
        tasks=[fetch_task, summarize_task, publish_task],
        process=Process.sequential,
        verbose=True,
        max_rpm=2
    )

    return crew


if __name__ == "__main__":
    crew = build_crew()
    # By default, use 'football' if no topic is provided in the environment
    news_topic = os.getenv("NEWS_TOPIC", "football")
    result = crew.kickoff(inputs={"topic": news_topic})
    print(result)
