import re
import html
import requests
from bs4 import BeautifulSoup
from typing import List
from app.models import BotSettings
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.retry_connection import retry_connection


@exception_handler()
def clean_text(text: str) -> str:
    """Cleans HTML tags and special characters from text."""
    text = html.unescape(text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@exception_handler()
@retry_connection()
def get_crypto_news_rss(url: str, news_amount: int = 5) -> List[str]:
    """
    Fetches the latest cryptocurrency news headlines and descriptions from an RSS feed.

    Args:
        url (str): The URL of the RSS feed.
        news_amount (int): The number of news articles to fetch per source.

    Returns:
        List[str]: A list of cleaned news headlines and summaries.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    news_items: List[str] = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")

        for item in soup.find_all("item")[:news_amount]:
            title = clean_text(item.title.text if item.title else "")
            description = clean_text(item.description.text if item.description else "")
            news_items.append(f"{title}: {description}")

    except Exception as e:
        logger.error(f"Failed to fetch news from {url}: {e}")

    return news_items


@exception_handler()
@retry_connection()
def fetch_all_crypto_news(bot_settings: object) -> str:
    """
    Fetches and aggregates crypto-related news from multiple RSS sources.

    Args:
         bot_settings (object): Bot settings object containing GPT model info.

    Returns:
        str: A summarized string of recent crypto headlines, ready for GPT prompt usage.
    """
    bot = BotSettings.query.get(bot_settings.id)
    news_urls = bot.news_sources
    limit_per_source = bot.news_limit_per_source
    total_limit = bot.news_total_limit
    all_news = []

    for url in news_urls:
        news = get_crypto_news_rss(url, limit_per_source)
        all_news.extend(news)

    seen = set()
    unique_news = []
    for n in all_news:
        if n not in seen:
            seen.add(n)
            unique_news.append(n)
        if len(unique_news) >= total_limit:
            break

    if not unique_news:
        return "There is no recent crypto and geopolitical news to consider."

    summary = " | ".join(unique_news)
    return f"Consider the following recent crypto and geopolitical news: {summary}"
