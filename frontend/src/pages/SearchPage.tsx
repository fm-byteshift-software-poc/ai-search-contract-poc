import { useState } from "react";
import SearchInput from "@/components/SearchInput";
import SearchResults from "@/components/SearchResults";
import type { SearchResponse } from "@/types/search";

export default function SearchPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);

  return (
    <div className="min-h-screen bg-base-100 pb-12">
      <header className="text-center pt-12 pb-8 px-4">
        <h1 className="text-3xl font-bold mb-2">AI Product Search PoC</h1>
        <p className="text-base-content/60 max-w-xl mx-auto">
          Type a natural language query to validate the search contract. 
          Results are ranked by explicit match signals and confidence bands.
        </p>
      </header>

      <SearchInput
        onSearch={setSearchResponse}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
      />

      <SearchResults response={searchResponse} />
    </div>
  );
}