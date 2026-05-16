# AI Product Search Contract PoC

## Overview

A zero-cost, contract-first prototype for AI-powered e-commerce search. This PoC validates the **integration surface, response schema, and fallback behavior** before production implementation. It focuses on deterministic evaluation, explicit intent parsing, and clean hand-off architecture.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Setup & Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

- **Swagger UI:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

---

## API Contract

### Endpoint

`POST /api/search/`

### Request Body

```json
{
  "query": "black running shoes under 100"
}
```

### Response Schema

The endpoint returns a strictly typed `SearchResponse` contract. `null` fields are explicitly included to guarantee schema stability for frontend integration.

| Field                | Type             | Purpose                                                        |
| -------------------- | ---------------- | -------------------------------------------------------------- |
| `query`              | `string`         | Original user input                                            |
| `parsed_intent`      | `object`         | Extracted constraints, confidence band, and parsing notes      |
| `results`            | `array`          | Ranked products with explicit `match_signals` and `score`      |
| `total_matches`      | `integer`        | Count of returned results                                      |
| `fallback_applied`   | `boolean`        | `true` if low confidence or zero matches triggered degradation |
| `fallback_reason`    | `string \| null` | Human-readable audit trail                                     |
| `processing_time_ms` | `float`          | Execution time for observability                               |
| `timestamp`          | `datetime`       | Response generation time                                       |

> 💡 **Integration note:** Frontend should validate against `parsed_intent.confidence` and `fallback_applied` before rendering results. `match_signals` can be used to highlight why a product ranked.

---

## Validation & Testing

Run these queries in Swagger or via `curl` to verify contract behavior:

| Query                             | Expected Behavior                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------- |
| `"black running shoes under 100"` | `confidence: high`, explicit filters extracted, `fallback_applied: false`             |
| `"wireless gaming mouse"`         | `confidence: high/medium`, category mapped, deterministic ranking                     |
| `"something cool for the office"` | `confidence: low`, `fallback_applied: true`, `score: 0.1`, explicit `fallback_reason` |

✅ **Contract is valid when:**

- All three cases return the same JSON structure
- `parsed_intent.constraints` reflect extracted filters (or `null`)
- `fallback_applied` and `fallback_reason` are explicit, never silent
- Zero runtime errors or missing fields

---

## Activating Real LLM Integration

This PoC runs in `mock` mode by default (zero cost, deterministic output). To activate OpenAI or Claude:

1. Copy configuration:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env`:
   ```env
   LLM_PROVIDER=openai  # or claude
   OPENAI_API_KEY=sk-proj-...
   # ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Update `src/routes/search.py` dependency injection:
   ```python
   # Replace hardcoded provider with env-driven config
   import os
   def get_search_service() -> SearchService:
       catalog = CatalogRepository()
       llm = LLMAdapter(provider=os.getenv("LLM_PROVIDER", "mock"))
       return SearchService(llm_adapter=llm, catalog=catalog)
   ```
4. Implement `_openai_parse()` or `_claude_parse()` in `src/utils/llm_adapter.py` using official SDKs. The `SearchService` contract requires **zero changes**.

> ⚠️ **Note:** Real LLM calls require API credits. Mock mode is sufficient for contract validation and demo staging.

---

## Architecture & Design Principles

| Principle                         | Implementation                                                                                                                            |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Contract-first**                | `SearchResponse` schema is defined before implementation. Frontend/backend agree on structure upfront.                                    |
| **LLM as translator, not engine** | The model only extracts intent & constraints. Filtering, ranking, and fallback are deterministic Python logic.                            |
| **Explicit degradation**          | `fallback_applied` + `fallback_reason` replace silent failures. Confidence bands guide frontend UX.                                       |
| **Mock by default**               | Zero-cost, reproducible outputs. Real LLM activation is a config toggle, not a rewrite.                                                   |
| **Integration-ready**             | Modular adapters, strict Pydantic validation, and observability fields (`processing_time_ms`, `timestamp`) survive production transplant. |

---

## Production Migration Path

When the MVP moves beyond prototype:

1. Replace `CatalogRepository` with SQL/NoSQL or search engine (Elastic/Meilisearch/Algolia)
2. Activate real LLM adapter + add rate limiting & token tracking
3. Add caching for identical queries & fallback responses
4. Instrument with structured logging, error tracing, and SLA alerts
5. Frontend integration: consume `/api/search/`, render `match_signals` as badges, handle `confidence: low` with placeholder UX

---

## License & Notes

- PoC artifact for contract validation only. Not production-optimized.
- Mock data intentionally covers edge cases (price boundaries, missing attributes, stock states, vague intent).
- Designed for clean hand-off: swap data layer + activate LLM → production-ready search surface.

---

## 👤 Maintained By

This project is developed and maintained by **FM ByteShift Software**

**Fernando Magalhães**  
CEO – FM ByteShift Software  
📞 (21) 97250-1546  
✉️ [contact@fmbyteshiftsoftware.com](mailto:contact@fmbyteshiftsoftware.com)  
🌐 [fmbyteshiftsoftware.com](https://fmbyteshiftsoftware.com)  
🏢 CNPJ: 62.145.022/0001-05 (Brazil)
