import os
from dotenv import load_dotenv
load_dotenv()

from tools.news_fetcher import NewsFetcherTool

if __name__ == "__main__":
    print("Testing NewsFetcherTool...")
    tool = NewsFetcherTool()
    
    # Try calling the run method
    result = tool._run(query="football news")
    
    print("\n--- Result ---")
    print(result)
    print("--------------")
