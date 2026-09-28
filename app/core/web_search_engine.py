"""
AetherMind Multimodal AI — Real-Time Web Search Engine
Provides free, API-less web search using DuckDuckGo HTML scraping.
Automatically triggered when the AI detects search-worthy queries in chat.
"""

import re
import urllib.parse
import httpx
from typing import List, Dict, Optional
from app.logging.logger import logger


class WebSearchEngine:
    """Free API-less Real-Time Web Search Engine powered by DuckDuckGo"""

    SEARCH_URL = "https://html.duckduckgo.com/html/"
    MAX_RESULTS = 5

    # Keywords that indicate the user wants real-time/current information
    SEARCH_TRIGGER_KEYWORDS = [
        "search for", "search about", "look up", "find out", "google",
        "latest news", "recent news", "current news", "today's",
        "what is the latest", "what happened", "who won", "score of",
        "weather in", "weather today", "stock price", "price of",
        "how to", "what is", "who is", "where is", "when is", "why is",
        "tell me about", "explain", "define", "meaning of",
        "best", "top 10", "top 5", "compare", "vs",
        "recipe for", "how do i", "tutorial",
        "2024", "2025", "2026", "2027",
        "release date", "launch date", "upcoming",
        "/search", "/web", "/browse",
    ]

    def should_search(self, prompt: str) -> bool:
        """Detect if the user's prompt requires a real-time web search."""
        p_lower = prompt.lower().strip()

        # Explicit search commands
        if p_lower.startswith(("/search", "/web", "/browse")):
            return True

        # Check for search trigger keywords
        for kw in self.SEARCH_TRIGGER_KEYWORDS:
            if kw in p_lower:
                return True

        # Questions that likely need current data
        if p_lower.endswith("?") and len(p_lower.split()) >= 3:
            question_starters = ["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does", "can", "will", "should"]
            first_word = p_lower.split()[0]
            if first_word in question_starters:
                return True

        return False

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Perform a real-time web search and return structured results."""
        results = []
        clean_query = query.strip()

        # Remove search command prefixes
        for prefix in ["/search ", "/web ", "/browse "]:
            if clean_query.lower().startswith(prefix):
                clean_query = clean_query[len(prefix):]

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.post(
                    self.SEARCH_URL,
                    data={"q": clean_query, "b": ""},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Referer": "https://duckduckgo.com/",
                    }
                )

                if resp.status_code == 200:
                    html = resp.text
                    results = self._parse_results(html, max_results)
                    logger.info(f"Web search for '{clean_query}' returned {len(results)} results")
                else:
                    logger.warning(f"DuckDuckGo search returned status {resp.status_code}")

        except Exception as e:
            logger.warning(f"Web search error: {e}")

        return results

    def _parse_results(self, html: str, max_results: int) -> List[Dict[str, str]]:
        """Parse DuckDuckGo HTML search results into structured data."""
        results = []

        # Extract result blocks using regex on the HTML
        # DuckDuckGo HTML results have class="result__a" for titles and class="result__snippet" for snippets
        title_pattern = re.compile(
            r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            re.DOTALL
        )
        snippet_pattern = re.compile(
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            re.DOTALL
        )

        titles = title_pattern.findall(html)
        snippets = snippet_pattern.findall(html)

        for i, (url, title) in enumerate(titles[:max_results]):
            # Clean HTML tags from title and snippet
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = ""
            if i < len(snippets):
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()

            # Decode DuckDuckGo redirect URL
            if "uddg=" in url:
                try:
                    real_url = urllib.parse.unquote(url.split("uddg=")[1].split("&")[0])
                    url = real_url
                except Exception:
                    pass

            if clean_title and url:
                results.append({
                    "title": clean_title,
                    "url": url,
                    "snippet": clean_snippet,
                    "source": self._extract_domain(url)
                })

        return results

    def _extract_domain(self, url: str) -> str:
        """Extract clean domain name from URL."""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain
        except Exception:
            return "web"

    def format_search_context(self, results: List[Dict[str, str]], query: str) -> str:
        """Format search results into a context block for the AI prompt."""
        if not results:
            return ""

        context_lines = [
            f"\n[WEB SEARCH RESULTS for: \"{query}\"]",
            "The following are real-time web search results. Use these to provide accurate, up-to-date answers. Cite sources when relevant.\n"
        ]

        for i, r in enumerate(results, 1):
            context_lines.append(f"[{i}] {r['title']}")
            if r['snippet']:
                context_lines.append(f"    {r['snippet']}")
            context_lines.append(f"    Source: {r['source']} — {r['url']}")
            context_lines.append("")

        context_lines.append("[END OF WEB SEARCH RESULTS]\n")
        return "\n".join(context_lines)


web_search_engine = WebSearchEngine()
