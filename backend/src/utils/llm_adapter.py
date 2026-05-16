import re
from typing import Callable

from src.models.product import (
    ParsedIntent,
    ParsedConstraints,
    ConfidenceBand,
    ProductCategory,
)


class LLMAdapter:
    """Abstraction layer for intent extraction. Decouples search service from specific LLM implementations."""

    def __init__(self, provider: str = "mock"):
        self.provider = provider.lower()
        self._handler: Callable[[str], ParsedIntent]
        self._init_handler()

    def _init_handler(self) -> None:
        if self.provider == "mock":
            self._handler = self._mock_parse
        elif self.provider == "openai":
            self._handler = self._openai_parse
        elif self.provider == "claude":
            self._handler = self._claude_parse
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def parse(self, query: str) -> ParsedIntent:
        """Extract structured intent from natural language query."""
        return self._handler(query)

    def _mock_parse(self, query: str) -> ParsedIntent:
        """Deterministic mock for PoC validation. Returns predictable contract structure."""
        q = query.lower()
        constraints = ParsedConstraints()
        notes = ["Mock intent extraction active"]

        # Intentional keyword mapping to demonstrate constraint extraction
        if any(kw in q for kw in ["tênis", "shoe", "sneaker", "running"]):
            constraints.category = ProductCategory.FOOTWEAR
        elif any(kw in q for kw in ["camiseta", "hoodie", "shirt", "moletom"]):
            constraints.category = ProductCategory.APPAREL
        elif any(kw in q for kw in ["mouse", "teclado", "keyboard", "gaming"]):
            constraints.category = ProductCategory.ELECTRONICS

        if any(kw in q for kw in ["preto", "black"]):
            constraints.color = "black"
        elif any(kw in q for kw in ["branco", "white"]):
            constraints.color = "white"

        price_match = re.search(r"(\d+)\s*(?:real|r\$|usd|\$)?", q)
        if price_match:
            constraints.price_max = float(price_match.group(1))

        # Confidence based on extraction completeness
        confidence = ConfidenceBand.LOW
        if constraints.price_max is not None:
            confidence = ConfidenceBand.MEDIUM
        if constraints.category:
            confidence = ConfidenceBand.HIGH

        if confidence == ConfidenceBand.LOW:
            notes.append("No explicit constraints detected. Falling back to broad catalog scan.")

        return ParsedIntent(
            original_query=query,
            constraints=constraints,
            confidence=confidence,
            parsing_notes=notes,
        )

    def _openai_parse(self, query: str) -> ParsedIntent:
        raise NotImplementedError("OpenAI adapter requires API key & structured output config.")

    def _claude_parse(self, query: str) -> ParsedIntent:
        raise NotImplementedError("Claude adapter requires API key & tool-use config.")