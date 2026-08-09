import os

from dotenv import load_dotenv
from langchain_community.tools import tool
import requests
from tavily import TavilyClient
from bs4 import BeautifulSoup

from readability import Document
import trafilatura
import re

load_dotenv()


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns title, url and snippet for each"""
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "Web search failed: missing TAVILY_API_KEY environment variable."

    try:
        tavily = TavilyClient(api_key=api_key)
        results = tavily.search(query=query, max_results=5)

        output = []

        for current_result in results.get("results", []):
            item = (
                f"Title: {current_result.get('title', 'Untitled')}\n"
                f"URL: {current_result.get('url', 'No URL returned')}\n"
                f"Snippet: {current_result.get('content', '')[:300]}\n"
            )
            output.append(item)

        if not output:
            return "Web search returned no results."

        return "\n-----\n".join(output)
    except Exception as e:
        return f"Web search failed: {e}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and extract clean readable content from a URL. Uses multiple extraction stratergies for better reliability."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        # Fetch page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        html = response.text

        # Extract stratergy 1, using trafilatura, best for blogs and articles
        extracted = trafilatura.extract(
            html, include_comments=False, include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", extracted)
            return cleaned[:5000]

        # Extract stratergy 2, using readability
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "form"]
        ):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", text)
            return cleaned[:5000]

        # Extract stratergy 2, full page extraction

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "form"]
        ):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        cleaned = re.sub(r"\s+", " ", text)

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."
    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."
    except requests.exceptions.HTTPError as e:
        return f"HTTP error occured: {str(e)}"
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
