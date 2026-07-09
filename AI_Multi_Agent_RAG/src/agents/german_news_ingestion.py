# src/agents/german_news_ingestion.py
# Fetches German news from free public sources
# No API key required for any of these sources

import requests
import feedparser
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup


# -------------------------------------------------------------------
# Free German news RSS feeds — no API key needed
# -------------------------------------------------------------------
GERMAN_NEWS_FEEDS = {
    "tagesschau": {
        "url": "https://www.tagesschau.de/xml/rss2",
        "language": "de",
        "category": "general"
    },
    "tagesschau_wirtschaft": {
        "url": "https://www.tagesschau.de/xml/rss2_wirtschaft",
        "language": "de",
        "category": "business"
    },
    "dw_german": {
        "url": "https://rss.dw.com/rdf/rss-de-all",
        "language": "de",
        "category": "international"
    },
    "zeit_politik": {
        "url": "https://newsfeed.zeit.de/politik/index",
        "language": "de",
        "category": "politics"
    },
    "heise_news": {
        "url": "https://www.heise.de/rss/heise-atom.xml",
        "language": "de",
        "category": "technology"
    },
    "dw_english": {
        "url": "https://rss.dw.com/rdf/rss-en-all",
        "language": "en",
        "category": "international"
    }
}


class GermanNewsIngestionAgent:
    """
    Fetches and processes German and English news from free RSS feeds.
    No API keys required.

    Sources:
    - Tagesschau (Germany's main public broadcaster)
    - Deutsche Welle (Germany's international broadcaster)
    - Zeit Online (major German newspaper)
    - Heise (German tech news)

    Produces chunks compatible with your existing RAG pipeline.
    """

    def __init__(self, max_articles_per_feed: int = 20):
        self.max_articles_per_feed = max_articles_per_feed
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; RAG-Pipeline/1.0)"
        })

    def _generate_chunk_id(self, url: str, title: str) -> str:
        """Generate unique ID for deduplication."""
        content = f"{url}_{title}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _fetch_rss_feed(
        self,
        feed_name: str,
        feed_config: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Fetches articles from a single RSS feed.
        Returns list of article dicts.
        """
        articles = []

        try:
            feed = feedparser.parse(feed_config["url"])

            for entry in feed.entries[:self.max_articles_per_feed]:
                # Extract clean text from description/summary
                raw_summary = entry.get("summary", entry.get("description", ""))

                # Strip HTML tags
                soup = BeautifulSoup(raw_summary, "html.parser")
                clean_summary = soup.get_text(separator=" ").strip()

                # Build full content: title + summary
                title = entry.get("title", "")
                full_content = f"{title}. {clean_summary}".strip()

                if len(full_content) < 50:
                    continue  # Skip empty articles

                # Parse publication date
                published = entry.get("published", "")
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).isoformat()

                article = {
                    "title": title,
                    "content": full_content,
                    "url": entry.get("link", ""),
                    "published": published,
                    "source": feed_name,
                    "language": feed_config["language"],
                    "category": feed_config["category"]
                }
                articles.append(article)

        except Exception as e:
            print(f"GermanNewsIngestionAgent: Error fetching {feed_name}: {e}")

        return articles

    def fetch_all_news(
        self,
        feeds: Dict[str, Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches news from all configured feeds.

        Args:
            feeds: Optional custom feed dict. Uses GERMAN_NEWS_FEEDS if None.

        Returns:
            List of article dicts
        """
        if feeds is None:
            feeds = GERMAN_NEWS_FEEDS

        all_articles = []
        seen_ids = set()

        for feed_name, feed_config in feeds.items():
            print(f"GermanNewsIngestionAgent: Fetching {feed_name}...")
            articles = self._fetch_rss_feed(feed_name, feed_config)

            # Deduplicate by content hash
            for article in articles:
                chunk_id = self._generate_chunk_id(
                    article["url"],
                    article["title"]
                )
                if chunk_id not in seen_ids:
                    seen_ids.add(chunk_id)
                    article["chunk_id"] = chunk_id
                    all_articles.append(article)

            print(f"GermanNewsIngestionAgent: Got {len(articles)} articles from {feed_name}")

        print(f"GermanNewsIngestionAgent: Total unique articles: {len(all_articles)}")
        return all_articles

    def convert_to_rag_chunks(
        self,
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Converts news articles into the chunk format
        compatible with your existing RAG pipeline.

        Output format matches PDFIngestionAgent output exactly
        so it can be passed directly to PreprocessorAgent
        and RetrieverAgent.
        """
        chunks = []

        for article in articles:
            chunk = {
                "chunk_id": article.get("chunk_id", self._generate_chunk_id(
                    article.get("url", ""),
                    article.get("title", "")
                )),
                "content": article["content"],
                "metadata": {
                    "source": article["source"],
                    "url": article.get("url", ""),
                    "title": article.get("title", ""),
                    "published": article.get("published", ""),
                    "category": article.get("category", "general"),
                    "page": "0",  # News articles don't have pages
                    "document_type": "news_article"
                },
                "language": article.get("language", "de")
            }
            chunks.append(chunk)

        # Language summary
        de_count = sum(1 for c in chunks if c["language"] == "de")
        en_count = sum(1 for c in chunks if c["language"] == "en")
        print(f"GermanNewsIngestionAgent: Created {len(chunks)} chunks")
        print(f"  German: {de_count} | English: {en_count}")

        return chunks

    def run(self) -> List[Dict[str, Any]]:
        """
        Full pipeline: fetch → deduplicate → convert to chunks.
        Returns RAG-ready chunks.
        """
        print("GermanNewsIngestionAgent: Starting news ingestion...")
        articles = self.fetch_all_news()
        chunks = self.convert_to_rag_chunks(articles)
        print("GermanNewsIngestionAgent: News ingestion complete.")
        return chunks


# -------------------------------------------------------------------
# Duplicate PDF detection — fixes the retrieval duplicate issue
# -------------------------------------------------------------------

def deduplicate_pdfs(pdf_paths: List[str]) -> List[str]:
    """
    Remove duplicate PDFs by comparing file content hashes.
    Fixes the 90ba854a-en.pdf / 90ba854a-en (1).pdf duplicate issue.

    Args:
        pdf_paths: List of PDF file paths

    Returns:
        Deduplicated list — keeps first occurrence of each unique file
    """
    import hashlib

    seen_hashes = set()
    unique_paths = []
    removed = []

    for path in pdf_paths:
        try:
            with open(path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            if file_hash not in seen_hashes:
                seen_hashes.add(file_hash)
                unique_paths.append(path)
            else:
                removed.append(path)
        except FileNotFoundError:
            print(f"WARNING: File not found, skipping: {path}")

    if removed:
        print(f"deduplicate_pdfs: Removed {len(removed)} duplicate(s):")
        for r in removed:
            print(f"  - {r}")

    print(f"deduplicate_pdfs: {len(unique_paths)} unique PDFs remaining.")
    return unique_paths
