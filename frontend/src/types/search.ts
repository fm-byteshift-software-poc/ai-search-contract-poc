export interface Product {
  id: string;
  name: string;
  description: string | null;
  price: number;
  category: ProductCategory;
  color: string | null;
  material: string | null;
  size: string | null;
  brand: string | null;
  in_stock: boolean;
  created_at: string;
  updated_at: string;
}

export type ProductCategory =
  | "footwear"
  | "apparel"
  | "electronics"
  | "accessories";

export interface ParsedConstraints {
  category: ProductCategory | null;
  color: string | null;
  material: string | null;
  size: string | null;
  brand: string | null;
  price_min: number | null;
  price_max: number | null;
  in_stock_only: boolean;
}

export type ConfidenceBand = "high" | "medium" | "low";

export interface ParsedIntent {
  original_query: string;
  constraints: ParsedConstraints;
  confidence: ConfidenceBand;
  parsing_notes: string[];
}

export interface MatchSignals {
  category_match: boolean;
  price_match: boolean;
  attribute_match: boolean;
  keyword_match: boolean;
}

export interface SearchResult {
  product: Product;
  score: number;
  match_signals: MatchSignals;
}

export interface SearchResponse {
  query: string;
  parsed_intent: ParsedIntent;
  results: SearchResult[];
  total_matches: number;
  fallback_applied: boolean;
  fallback_reason: string | null;
  processing_time_ms: number | null;
  timestamp: string;
}

export interface SearchRequest {
  query: string;
}
