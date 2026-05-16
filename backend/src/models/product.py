from uuid import UUID, uuid4
from datetime import datetime, timezone
from enum import StrEnum
from pydantic import BaseModel, Field


class ProductCategory(StrEnum):
    FOOTWEAR = "footwear"
    APPAREL = "apparel"
    ELECTRONICS = "electronics"
    ACCESSORIES = "accessories"


class Product(BaseModel):
    """Core product entity reflecting typical e-commerce attributes for search filtering."""
    
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str | None = None
    price: float = Field(ge=0)
    category: ProductCategory
    color: str | None = None
    material: str | None = None
    size: str | None = None
    brand: str | None = None
    in_stock: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ParsedConstraints(BaseModel):
    """Structured filters extracted from natural language query."""
    
    category: ProductCategory | None = None
    color: str | None = None
    material: str | None = None
    size: str | None = None
    brand: str | None = None
    price_min: float | None = Field(default=None, ge=0)
    price_max: float | None = Field(default=None, ge=0)
    in_stock_only: bool = False


class ConfidenceBand(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ParsedIntent(BaseModel):
    """Output contract for query interpretation layer."""
    
    original_query: str
    constraints: ParsedConstraints
    confidence: ConfidenceBand
    parsing_notes: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Individual result with explicit relevance signals."""
    
    product: Product
    score: float = Field(ge=0, le=1)
    match_signals: dict[str, bool] = Field(
        default_factory=lambda: {
            "category_match": False,
            "price_match": False,
            "attribute_match": False,
            "keyword_match": False,
        }
    )


class SearchResponse(BaseModel):
    """Full integration contract for search endpoint."""
    
    query: str
    parsed_intent: ParsedIntent
    results: list[SearchResult]
    total_matches: int
    fallback_applied: bool = False
    fallback_reason: str | None = None
    processing_time_ms: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))