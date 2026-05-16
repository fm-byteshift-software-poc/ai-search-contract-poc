from uuid import UUID
from datetime import datetime, timezone

from src.models.product import Product, ProductCategory

# Static timestamp for deterministic PoC runs
_NOW = datetime(2026, 5, 16, 10, 0, 0, tzinfo=timezone.utc)


class CatalogRepository:
    """Data access layer for product catalog. 
    Starts with deterministic mock data aligned to real e-commerce schemas. 
    Ready for drop-in replacement with SQL/NoSQL repository."""

    def __init__(self, products: list[Product] | None = None):
        self._products = products if products is not None else self._load_mock_catalog()

    def get_all(self) -> list[Product]:
        """Returns a defensive copy to prevent external mutation."""
        return list(self._products)

    def _load_mock_catalog(self) -> list[Product]:
        """Strategic mock set designed to validate constraint parsing, fallback behavior, and edge cases."""
        return [
            # Matches: "black running shoes under $100"
            Product(id=UUID("11111111-1111-4111-8111-111111111111"), name="UltraBoost Running Shoe", price=89.99, category=ProductCategory.FOOTWEAR, color="black", material="mesh", size="42", brand="adidas", in_stock=True, created_at=_NOW, updated_at=_NOW),
            # Price boundary test: exactly at limit
            Product(id=UUID("22222222-2222-4222-8222-222222222222"), name="Budget Trail Runner", price=100.00, category=ProductCategory.FOOTWEAR, color="grey", material="synthetic", size="40", brand="generic", in_stock=True, created_at=_NOW, updated_at=_NOW),
            # Over-limit test: should be excluded by price_max filter
            Product(id=UUID("33333333-3333-4333-8333-333333333333"), name="Premium Leather Sneaker", price=120.00, category=ProductCategory.FOOTWEAR, color="black", material="leather", size="41", brand="nike", in_stock=True, created_at=_NOW, updated_at=_NOW),
            
            # Matches: "wireless gaming mouse"
            Product(id=UUID("44444444-4444-4444-8444-444444444444"), name="Wireless Gaming Mouse", price=45.50, category=ProductCategory.ELECTRONICS, color="black", material="plastic", brand="logitech", in_stock=True, created_at=_NOW, updated_at=_NOW),
            # Missing attributes test: color/material None
            Product(id=UUID("55555555-5555-4555-8555-555555555555"), name="Mechanical Keyboard RGB", price=99.00, category=ProductCategory.ELECTRONICS, color=None, material="aluminum", brand="corsair", in_stock=True, created_at=_NOW, updated_at=_NOW),
            
            # Matches: "minimalist white hoodie"
            Product(id=UUID("66666666-6666-4666-8666-666666666666"), name="Minimalist White Hoodie", price=65.00, category=ProductCategory.APPAREL, color="white", material="cotton", size="M", brand="zara", in_stock=True, created_at=_NOW, updated_at=_NOW),
            # Out-of-stock test: should be excluded if in_stock_only=True
            Product(id=UUID("77777777-7777-4777-8777-777777777777"), name="Heavy Cotton T-Shirt", price=29.99, category=ProductCategory.APPAREL, color="black", material="cotton", size="L", brand="uniqlo", in_stock=False, created_at=_NOW, updated_at=_NOW),
            
            # Fallback trigger test: vague query won't match strict constraints
            Product(id=UUID("88888888-8888-4888-8888-888888888888"), name="Premium Leather Belt", price=110.00, category=ProductCategory.ACCESSORIES, color="brown", material="leather", brand="herschel", in_stock=True, created_at=_NOW, updated_at=_NOW),
            Product(id=UUID("99999999-9999-4999-8999-999999999999"), name="Wireless Earbuds", price=79.99, category=ProductCategory.ELECTRONICS, color="white", material="silicone", brand="samsung", in_stock=True, created_at=_NOW, updated_at=_NOW),
        ]