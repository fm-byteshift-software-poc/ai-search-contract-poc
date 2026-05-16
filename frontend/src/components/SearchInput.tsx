import { useState } from "react";
import { searchService } from "@/services/searchService";
import type { SearchResponse } from "@/types/search";

interface SearchInputProps {
  onSearch: (results: SearchResponse) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export default function SearchInput({ onSearch, isLoading, setIsLoading }: SearchInputProps) {
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const results = await searchService.search(query.trim());
      onSearch(results);
    } catch {
      setError("Failed to fetch search results. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto my-8 space-y-3">
      <div className="join w-full shadow-sm">
        <input
          type="text"
          className="input join-item w-full input-lg"
          placeholder="e.g. black running shoes under 100"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn join-item btn-primary btn-lg"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? <span className="loading loading-spinner"></span> : "Search"}
        </button>
      </div>
      {error && <p className="text-error text-sm text-center">{error}</p>}
    </form>
  );
}