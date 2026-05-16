import time
from datetime import datetime, timezone

from src.models.product import (
    Product, ParsedIntent, ParsedConstraints, SearchResponse, SearchResult, ConfidenceBand
)
from src.utils.llm_adapter import LLMAdapter
from src.repositories.catalog_repository import CatalogRepository


class SearchService:
    """Core search orchestration layer. Decouples intent extraction from deterministic filtering/ranking."""

    def __init__(self, llm_adapter: LLMAdapter, catalog: CatalogRepository):
        self.llm_adapter = llm_adapter
        self.catalog = catalog

    def search(self, query: str) -> SearchResponse:
        start_time = time.perf_counter()
        
        # 1. Intent extraction (mock or real LLM)
        parsed_intent = self._parse_query(query)
        
        # 2. Deterministic filtering & scoring
        matched_products = self._filter_and_rank(parsed_intent.constraints)
        
        # 3. Fallback handling if extraction was uncertain or no matches found
        if parsed_intent.confidence == ConfidenceBand.LOW or not matched_products:
            matched_products = self._apply_fallback(query, parsed_intent)
        
        # 4. Contract assembly
        processing_time_ms = (time.perf_counter() - start_time) * 1000
        return self._build_response(query, parsed_intent, matched_products, processing_time_ms)

    def _parse_query(self, query: str) -> ParsedIntent:
        """Delegates to LLM adapter. Returns validated ParsedIntent or graceful degradation."""
        return self.llm_adapter.parse(query)

    def _filter_and_rank(self, constraints: ParsedConstraints) -> list[SearchResult]:
        """Applies extracted constraints to catalog, calculates signals & deterministic scores."""
        results = []
        catalog = self.catalog.get_all()

        for product in catalog:
            if not self._matches_constraints(product, constraints):
                continue

            signals = self._calculate_match_signals(product, constraints)
            score = self._calculate_score(product, constraints, signals)
            results.append(SearchResult(product=product, score=score, match_signals=signals))

        # Sort by score descending, then by price ascending as tie-breaker
        results.sort(key=lambda r: (-r.score, r.product.price))
        return results

    def _matches_constraints(self, product: Product, constraints: ParsedConstraints) -> bool:
        """Hard filter gate. If a strict constraint fails, product is excluded."""
        if constraints.in_stock_only and not product.in_stock:
            return False
        if constraints.category and product.category != constraints.category:
            return False
        if constraints.price_max is not None and product.price > constraints.price_max:
            return False
        if constraints.price_min is not None and product.price < constraints.price_min:
            return False
        return True

    def _calculate_match_signals(self, product: Product, constraints: ParsedConstraints) -> dict[str, bool]:
        """Explicit boolean signals explaining WHY a product matched."""
        return {
            "category_match": constraints.category == product.category,
            "price_match": (
                (constraints.price_min is None or product.price >= constraints.price_min) and
                (constraints.price_max is None or product.price <= constraints.price_max)
            ),
            "attribute_match": bool(
                (not constraints.color or product.color == constraints.color) and
                (not constraints.brand or product.brand == constraints.brand) and
                (not constraints.material or product.material == constraints.material)
            ),
            "keyword_match": True  # Reserved for future text-search integration
        }

    def _calculate_score(self, product: Product, constraints: ParsedConstraints, signals: dict[str, bool]) -> float:
        """Deterministic 0.0–1.0 score based on constraint match density & price proximity."""
        weights = {"category_match": 0.4, "price_match": 0.3, "attribute_match": 0.2, "keyword_match": 0.1}
        base_score = sum(weights[k] * (1.0 if v else 0.0) for k, v in signals.items())

        # Bonus for price proximity
        if constraints.price_max and product.price <= constraints.price_max:
            base_score += 0.05

        return round(min(max(base_score, 0.0), 1.0), 2)

    def _apply_fallback(self, query: str, intent: ParsedIntent) -> list[SearchResult]:
        """Graceful degradation: returns top catalog items with clear audit trail."""
        top_items = self.catalog.get_all()[:5]
        intent.parsing_notes.append("Fallback applied due to low confidence or empty match set")
        return [
            SearchResult(
                product=prod, 
                score=0.1, 
                match_signals={k: False for k in ["category_match", "price_match", "attribute_match", "keyword_match"]}
            )
            for prod in top_items
        ]

    def _build_response(self, query: str, intent: ParsedIntent, results: list[SearchResult], time_ms: float) -> SearchResponse:
        """Assembles final integration contract with observability & fallback metadata."""
        fallback = intent.confidence == ConfidenceBand.LOW or not results
        return SearchResponse(
            query=query,
            parsed_intent=intent,
            results=results,
            total_matches=len(results),
            fallback_applied=fallback,
            fallback_reason="Low parsing confidence or no exact matches" if fallback else None,
            processing_time_ms=round(time_ms, 2),
            timestamp=datetime.now(timezone.utc)
        )