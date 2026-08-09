from src.pipelines.pipelines import run_research_pipeline
from src.tools.tools import web_search, scrape_url


def main():

    topic = "The impact of AI on the job market in 2026"
    run_research_pipeline(topic)


if __name__ == "__main__":
    main()
