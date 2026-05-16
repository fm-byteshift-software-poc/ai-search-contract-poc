# AI Product Search Contract PoC

> **Important Expectation Notice**  
> This PoC demonstrates the **integration contract and deterministic pipeline** for AI-powered search. By default, it runs in **mock mode** (zero cost, fully reproducible) to validate schema, fallback behavior, and frontend/backend hand-off. **No real LLM calls are made** unless explicitly activated via configuration. This is intentional: we prove the architecture works before adding variable-cost AI.

---

## What This PoC Proves

| Validated                                              | Not Included (Yet)                        |
| ------------------------------------------------------ | ----------------------------------------- |
| Strict `SearchResponse` contract (backend to frontend) | Real OpenAI/Claude API calls              |
| Deterministic intent parsing to filtering to ranking   | Production-scale catalog (10k+ SKUs)      |
| Explicit fallback behavior and confidence bands        | Vector search, embeddings, or RAG         |
| Frontend consumes contract with type safety            | Authentication, payments, admin dashboard |
| Zero-cost local execution                              | Deployment, CI/CD, monitoring             |

**In short:** This is a **specification executable**, not a production search engine. It proves _how_ AI search will integrate. The semantic intelligence layer is added after the contract is validated.

---

## Quick Start (Full Stack)

### Prerequisites

- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- Git

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn src.main:app --reload
```

Check the terminal output for the server URL (typically `http://localhost:8000`). Access the health endpoint to confirm the service is running.

### 2. Frontend (Vite + React + TypeScript + DaisyUI)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Check the terminal output for the dev server URL (typically `http://localhost:5173`). Open this URL in your browser to access the UI.

### 3. Test End-to-End

Open the frontend URL from the terminal and try:

```
"black running shoes under 100"  → high confidence, filtered results
"wireless gaming mouse"          → electronics category mapped
"algo legal pro escritório"      → fallback mode, explicit warning
```

---

## Live Demo

This PoC is publicly accessible for validation and stakeholder review:

- **Frontend (Vercel):** https://ai-search-contract-poc.vercel.app/
- **Backend API (Render):** https://ai-search-contract-poc-api.onrender.com
- **API Documentation (Swagger):** https://ai-search-contract-poc-api.onrender.com/docs

### Free Tier Notice

Both deployments use free-tier infrastructure. Please note:

1. **Cold starts**: If the backend has not received traffic in the last 15 minutes, Render may put the service to sleep. The first request can take 30–60 seconds to "wake up" the instance. This is expected behavior and does not indicate an error.

2. **Frontend latency**: Vercel's free tier may also experience brief initialization delays on first load after periods of inactivity.

3. **Rate limits**: Free tiers have request quotas. If you encounter `429 Too Many Requests`, wait a few minutes before retrying.

### Testing Recommendations

- Allow up to 60 seconds for the first search query to complete after a period of inactivity
- Subsequent requests will respond normally (typically under 200ms)
- If the frontend shows a network error, wait 30 seconds and retry once
- For consistent demo performance, keep a browser tab open to the backend URL to prevent sleep

> This deployment is for PoC validation only. Production deployments would use dedicated infrastructure with auto-scaling, caching, and SLA-backed uptime.

---

## How the Search Actually Works (Mock Mode)

### The Pipeline (Deterministic, No LLM)

```
User Query
   ↓
[Mock Parser] ← Keyword mapping, regex extraction (no AI)
   ↓
ParsedIntent { constraints, confidence, notes }
   ↓
[Filter Engine] ← Python logic: category/price/attribute gates
   ↓
[Ranking] ← Weighted score: category(40%) + price(30%) + attributes(20%) + keyword(10%)
   ↓
[Contract Assembly] ← Pydantic validation → SearchResponse JSON
   ↓
Frontend renders results + match_signals badges
```

### Why Mock First?

1. **Zero cost**: No API keys, no credits, no surprises
2. **Reproducible**: Same query produces the same result, enabling reliable demos
3. **Contract-focused**: Forces agreement on output shape before optimizing "intelligence"
4. **Safe fallback testing**: We can trigger `confidence: low` on demand to validate UX

### When You Activate Real LLM

1. Set `LLM_PROVIDER=openai` in backend `.env`
2. Add your API key
3. Implement `_openai_parse()` in `src/utils/llm_adapter.py` (structured output)
4. **Everything else stays identical**: service, contract, frontend, tests

The LLM only replaces the `[Mock Parser]` component. The rest of the pipeline is production-ready.

---

## API Contract (Backend to Frontend)

### Endpoint

`POST /api/search`

### Request

```json
{ "query": "black running shoes under 100" }
```

### Response (`SearchResponse`)

```typescript
{
  query: string;
  parsed_intent: {
    original_query: string;
    constraints: { category?, color?, price_min?, price_max?, ... };
    confidence: "high" | "medium" | "low";
    parsing_notes: string[];
  };
  results: Array<{
    product: { id, name, price, category, color?, brand?, ... };
    score: number; // 0.0–1.0
    match_signals: { category_match, price_match, attribute_match, keyword_match };
  }>;
  total_matches: number;
  fallback_applied: boolean;
  fallback_reason: string | null;
  processing_time_ms: number | null;
  timestamp: string; // ISO 8601
}
```

> **Frontend integration tip**: Use `parsed_intent.confidence` to show trust indicators, and `match_signals` to render badges explaining _why_ a product ranked.

---

## Validation Checklist

Run these queries and verify:

| Query                             | Expected Contract Behavior                                                                            |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `"black running shoes under 100"` | `confidence: "high"`, `price_max: 100`, `fallback_applied: false`, results less than or equal to $100 |
| `"wireless gaming mouse"`         | `category: "electronics"`, 3+ electronics items, `score` weighted by match_signals                    |
| `"algo legal pro escritório"`     | `confidence: "low"`, `fallback_applied: true`, alert banner visible, scores = 0.1                     |

**Contract is valid when**:

- All responses follow the exact `SearchResponse` schema (no missing fields)
- `null` values are explicit (not omitted)
- `fallback_applied` never hides uncertainty
- Frontend TypeScript compiles with zero `any` or `@ts-ignore`

---

## Activating Real LLM (When Ready)

1. **Backend config** (`backend/.env`):

   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-...
   ```

2. **Update dependency injection** (`backend/src/routes/search.py`):

   ```python
   import os
   def get_search_service():
       catalog = CatalogRepository()
       llm = LLMAdapter(provider=os.getenv("LLM_PROVIDER", "mock"))
       return SearchService(llm_adapter=llm, catalog=catalog)
   ```

3. **Implement adapter** (`backend/src/utils/llm_adapter.py`):
   - Use OpenAI/Claude SDK with structured output (JSON mode / tool use)
   - Return `ParsedIntent` matching the mock's schema exactly

4. **Test**: Same queries, same contract — now with semantic understanding

> **Cost note**: Real LLM calls incur per-request charges. Mock mode is free and sufficient for contract validation, stakeholder demos, and frontend integration testing.

---

## Architecture Snapshot

```
frontend/                          backend/
├─ src/                            ├─ src/
│  ├─ types/search.ts  ← Contract │  ├─ models/product.py  ← Contract
│  ├─ services/searchService.ts   │  ├─ utils/llm_adapter.py  ← Mock/Real switch
│  ├─ components/                 │  ├─ repositories/catalog_repository.py
│  │  ├─ SearchInput.tsx          │  ├─ services/search_service.py  ← Pipeline
│  │  ├─ SearchResults.tsx        │  ├─ routes/search.py  ← POST /api/search
│  │  └─ ...                      │  └─ main.py  ← CORS, app factory
│  └─ pages/SearchPage.tsx        └─ requirements.txt
├─ .env.example                    └─ .env.example
└─ vite.config.ts
```

**Key principle**: The contract (`SearchResponse` / `search.ts`) is the single source of truth. Change the parser (mock to LLM) or the data layer (mock list to SQL) without touching the rest.

> **PoC Scope Reminder**: This artifact is for contract validation and stakeholder alignment only. It is not optimized for production scale, security hardening, or cost-efficient LLM usage. Those concerns are addressed in the post-MVP phase, using this PoC as the integration blueprint.

---

## 👤 Maintained By

This project is developed and maintained by **FM ByteShift Software**

**Fernando Magalhães**  
CEO – FM ByteShift Software  
📞 (21) 97250-1546  
✉️ [contact@fmbyteshiftsoftware.com](mailto:contact@fmbyteshiftsoftware.com)  
🌐 [fmbyteshiftsoftware.com](https://fmbyteshiftsoftware.com)  
🏢 CNPJ: 62.145.022/0001-05 (Brazil)
