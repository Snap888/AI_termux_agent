from typing import Dict

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class WebSearchTools:
    def __init__(self, config: Dict):
        self.enabled = config.get("agent", {}).get("enable_web_search", True)

    def web_search(self, query: str, max_results: int = 5) -> str:
        if not self.enabled:
            return "Web search is disabled in config"
        if DDGS is None:
            return "duckduckgo-search package not installed"

        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(
                        f"Title: {r.get('title')}\n"
                        f"URL: {r.get('href')}\n"
                        f"Snippet: {r.get('body')}\n"
                    )
            return "\n---\n".join(results) if results else "No results found"
        except Exception as e:
            return f"Search error: {e}"

    def as_dict(self):
        return {"web_search": self.web_search}
