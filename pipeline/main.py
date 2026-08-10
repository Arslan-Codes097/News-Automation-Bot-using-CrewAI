import os
from dotenv import load_dotenv
load_dotenv()
from crewai import Agent, Task, Crew, Process, LLM
from tools.news_fetcher import NewsFetcherTool
from tools.summarizer import SummarizerTool
from tools.slack_tool import SlackTool
from tools.sheets_logger import SheetsLoggerTool


def build_crew():
    llm_researcher = LLM(model="gemini/gemini-flash-latest", api_key=os.getenv("GEMINI_API_KEY"))
    llm_summarizer = LLM(model="gemini/gemini-flash-latest", api_key=os.getenv("GEMINI_API_KEY"))
    llm_publisher = LLM(model="gemini/gemini-flash-latest", api_key=os.getenv("GEMINI_API_KEY"))

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
        verbose=False,
        max_rpm=14
    )

    summarizer = Agent(
        role="{topic} News Summarizer",
        goal="Turn raw {topic} articles into short, clear summaries",
        backstory="A sharp editor who condenses stories into quick, readable updates without losing key facts.",
        tools=[summarizer_tool],
        llm=llm_summarizer,
        verbose=False,
        max_rpm=14
    )

    publisher = Agent(
        role="News Publisher",
        goal="Distribute summarized {topic} news to Slack and log it to Google Sheets",
        backstory="A newsroom assistant responsible for getting finished updates out to the team and keeping records.",
        tools=[slack_tool, sheets_tool],
        llm=llm_publisher,
        verbose=False,
        max_rpm=14
    )

    fetch_task = Task(
        description="Search for the latest news using the query '{topic} news today'. Return a maximum of 3 raw articles with titles, links, and snippets. Do not exceed this limit.",
        expected_output="A list of {topic} news articles with title, source, link, and snippet for each.",
        agent=researcher
    )

    summarize_task = Task(
        description="Take the 3 fetched articles and summarize EACH ONE into a short, clear 2-3 sentence update. You MUST output exactly 3 separate summaries. Remove duplicate stories covering the same event.",
        expected_output="A list of exactly 3 summarized {topic} updates, each with headline, summary, and source link.",
        agent=summarizer,
        context=[fetch_task]
    )

    publish_task = Task(
        description="You have received 3 summarized updates. YOU MUST USE YOUR TOOLS. Call the 'slack_poster' tool exactly 3 times (once for each article). Then, call the 'sheets_logger' tool exactly 3 times. DO NOT write the summaries in your final output; you must literally call the functions! If you don't call the tools, the user will not receive the news.",
        expected_output="Confirmation that exactly 3 updates were posted via tool calls.",
        agent=publisher,
        context=[summarize_task]
    )

    crew = Crew(
        agents=[researcher, summarizer, publisher],
        tasks=[fetch_task, summarize_task, publish_task],
        process=Process.sequential,
        verbose=False
    )

    return crew


if __name__ == "__main__":
    crew = build_crew()
    # By default, use 'football' if no topic is provided in the environment
    news_topic = os.getenv("NEWS_TOPIC", "football")
    result = crew.kickoff(inputs={"topic": news_topic})
    print(result)
