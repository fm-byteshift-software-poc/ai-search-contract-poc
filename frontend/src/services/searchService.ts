import api from "@/lib/api";
import type { SearchResponse } from "@/types/search";

export const searchService = {
  /**
   * Executes a natural language search query against the AI contract endpoint.
   */
  search: async (query: string): Promise<SearchResponse> => {
    // The backend expects { query: "..." } and returns the SearchResponse contract
    const { data } = await api.post<SearchResponse>("/api/search", { query });
    return data;
  },
};
