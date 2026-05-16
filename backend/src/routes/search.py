from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.models.product import SearchResponse
from src.services.search_service import SearchService
from src.repositories.catalog_repository import CatalogRepository
from src.utils.llm_adapter import LLMAdapter

router = APIRouter(prefix="/api/search", tags=["Search"])


class SearchRequest(BaseModel):
    """Standardized input contract for search queries."""
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        description="Natural language product query"
    )


def get_search_service() -> SearchService:
    """PoC dependency wiring. Swappable for DI container or env-driven config later."""
    catalog = CatalogRepository()
    llm = LLMAdapter(provider="mock")
    return SearchService(llm_adapter=llm, catalog=catalog)


@router.post(
    "/", 
    response_model=SearchResponse, 
    response_model_exclude_none=False
)
async def search_products(
    req: SearchRequest,
    service: SearchService = Depends(get_search_service),
):
    """Executes the search pipeline and returns the validated integration contract."""
    try:
        return service.search(req.query)
    except Exception as e:
        # Route-level safety net. Production would log, trace, and return a structured fallback.
        raise HTTPException(status_code=500, detail="Search processing failed") from e