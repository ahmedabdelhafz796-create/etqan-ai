"""News providers (§6 MASTER_PLAN) — NewsAPI, RSS feeds."""

import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from gold_agent.core.models import NewsItem


class NewsProvider(ABC):
    """Abstract news provider."""

    @abstractmethod
    async def fetch(self) -> List[NewsItem]:
        """Fetch latest news items."""
        pass


class MockNewsProvider(NewsProvider):
    """Mock news provider for testing (no API keys required)."""

    def __init__(self):
        self.mock_headlines = [
            {
                "title": "Federal Reserve Signals Pause on Rate Hikes",
                "description": "The Fed may hold rates steady amid cooling inflation.",
                "sentiment": 0.4,
            },
            {
                "title": "Gold Surges as Dollar Weakens",
                "description": "Precious metals rally on softer US currency.",
                "sentiment": 0.7,
            },
            {
                "title": "Inflation Data Disappoints Markets",
                "description": "Latest CPI reading comes in higher than expected.",
                "sentiment": -0.5,
            },
            {
                "title": "Banking Sector Faces Headwinds",
                "description": "Regional banks show weakness amid rate concerns.",
                "sentiment": -0.3,
            },
            {
                "title": "Geopolitical Tensions Rise",
                "description": "Global events drive demand for safe-haven assets like gold.",
                "sentiment": 0.6,
            },
            {
                "title": "Economic Growth Slows",
                "description": "GDP growth disappoints; investors seek safe haven.",
                "sentiment": 0.3,
            },
        ]
        self.random = random.Random(42)

    async def fetch(self) -> List[NewsItem]:
        """Return random mock news items."""
        num_items = self.random.randint(2, 4)
        items = []

        for i in range(num_items):
            headline = self.random.choice(self.mock_headlines)
            items.append(
                NewsItem(
                    timestamp=datetime.utcnow(),
                    title=headline["title"],
                    description=headline["description"],
                    source="mock",
                    url=None,
                    sentiment=headline["sentiment"],
                )
            )

        return items


class NewsAPIProvider(NewsProvider):
    """NewsAPI provider (production)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.last_error = None

    async def fetch(self) -> List[NewsItem]:
        """Fetch from NewsAPI."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                # Search for gold, currency, and macro-economic news
                queries = ["gold price", "dollar index", "interest rates", "inflation", "Fed"]
                all_articles = []

                for query in queries:
                    response = await session.get(
                        f"{self.base_url}/everything",
                        params={
                            "q": query,
                            "sortBy": "publishedAt",
                            "language": "en",
                            "apikey": self.api_key,
                            "pageSize": 5,
                        }
                    )

                    if response.status == 200:
                        data = await response.json()
                        if "articles" in data:
                            all_articles.extend(data["articles"])
                    elif response.status == 426:  # Too many requests
                        self.last_error = "Rate limited"
                        break

                # Convert to NewsItem objects with sentiment
                news_items = []
                for article in all_articles[:10]:  # Limit to 10 most recent
                    sentiment = self._estimate_sentiment(
                        article.get("title", "") + " " + article.get("description", "")
                    )
                    news_items.append(
                        NewsItem(
                            timestamp=datetime.fromisoformat(article.get("publishedAt", "").replace("Z", "+00:00")),
                            title=article.get("title", ""),
                            description=article.get("description", ""),
                            source=article.get("source", {}).get("name", "Unknown"),
                            url=article.get("url"),
                            sentiment=sentiment,
                        )
                    )

                return news_items
        except Exception as e:
            self.last_error = str(e)
            print(f"NewsAPI fetch error: {e}")

        return []

    def _estimate_sentiment(self, text: str) -> float:
        """Simple sentiment estimation using keyword matching."""
        positive_keywords = ["surge", "rally", "gain", "positive", "strength", "recovery", "beat", "exceeds", "higher"]
        negative_keywords = ["plunge", "crash", "fall", "negative", "weakness", "miss", "disappoints", "lower", "decline"]

        text_lower = text.lower()
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

        if positive_count == 0 and negative_count == 0:
            return 0.0

        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return max(-1.0, min(1.0, sentiment))


class RSSFeedProvider(NewsProvider):
    """RSS feed provider (production)."""

    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls or [
            "https://feeds.bloomberg.com/markets/commodities.rss",
            "https://feeds.cnbc.com/cnbc/financials",
            "http://feeds.reuters.com/reuters/businessNews",
        ]
        self.last_error = None

    async def fetch(self) -> List[NewsItem]:
        """Fetch from RSS feeds."""
        import aiohttp
        import xml.etree.ElementTree as ET
        from urllib.parse import urlparse

        news_items = []

        for feed_url in self.feed_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    response = await session.get(feed_url, timeout=aiohttp.ClientTimeout(total=5))

                    if response.status == 200:
                        content = await response.text()
                        root = ET.fromstring(content)

                        # Handle RSS 2.0 format
                        for item in root.findall(".//item")[:5]:  # Limit to 5 items per feed
                            title_elem = item.find("title")
                            desc_elem = item.find("description")
                            pubdate_elem = item.find("pubDate")
                            link_elem = item.find("link")

                            if title_elem is not None:
                                title = title_elem.text or ""
                                description = desc_elem.text if desc_elem is not None else ""
                                url = link_elem.text if link_elem is not None else None

                                # Parse publication date (RSS uses RFC 2822 format)
                                timestamp = datetime.utcnow()
                                if pubdate_elem is not None:
                                    try:
                                        from email.utils import parsedate_to_datetime
                                        timestamp = parsedate_to_datetime(pubdate_elem.text)
                                    except:
                                        pass

                                sentiment = self._estimate_sentiment(title + " " + description)

                                news_items.append(
                                    NewsItem(
                                        timestamp=timestamp,
                                        title=title,
                                        description=description,
                                        source=urlparse(feed_url).netloc,
                                        url=url,
                                        sentiment=sentiment,
                                    )
                                )
            except Exception as e:
                self.last_error = str(e)
                print(f"RSS feed error for {feed_url}: {e}")
                continue

        return sorted(news_items, key=lambda x: x.timestamp, reverse=True)[:10]

    def _estimate_sentiment(self, text: str) -> float:
        """Simple sentiment estimation using keyword matching."""
        positive_keywords = ["surge", "rally", "gain", "positive", "strength", "recovery", "beat", "exceeds", "higher"]
        negative_keywords = ["plunge", "crash", "fall", "negative", "weakness", "miss", "disappoints", "lower", "decline"]

        text_lower = text.lower()
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

        if positive_count == 0 and negative_count == 0:
            return 0.0

        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return max(-1.0, min(1.0, sentiment))


def get_news_provider(provider_type: str, **kwargs) -> NewsProvider:
    """Factory function to get news provider."""
    if provider_type == "mock":
        return MockNewsProvider()
    elif provider_type == "newsapi":
        return NewsAPIProvider(kwargs.get("api_key"))
    elif provider_type == "rss":
        return RSSFeedProvider(kwargs.get("feed_urls", []))
    else:
        raise ValueError(f"Unknown news provider: {provider_type}")
