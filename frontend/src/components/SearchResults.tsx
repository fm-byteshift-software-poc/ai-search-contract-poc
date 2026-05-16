import type { SearchResponse, MatchSignals } from "@/types/search";

interface SearchResultsProps {
  response: SearchResponse | null;
}

function MatchBadges({ signals }: { signals: MatchSignals }) {
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {Object.entries(signals).map(([key, matched]) => (
        <span
          key={key}
          className={`badge badge-sm ${
            matched ? "badge-primary" : "badge-ghost"
          }`}
        >
          {key.replace(/_/g, " ")} {matched ? "✓" : "–"}
        </span>
      ))}
    </div>
  );
}

export default function SearchResults({ response }: SearchResultsProps) {
  if (!response) return null;

  // Fallback state visualization
  if (response.fallback_applied) {
    return (
      <div role="alert" className="alert alert-warning shadow-sm mt-8 max-w-2xl mx-auto">
        <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <div>
          <h3 className="font-bold">Fallback Mode Active</h3>
          <p className="text-sm">{response.fallback_reason || "Low parsing confidence or no exact matches found."}</p>
        </div>
      </div>
    );
  }

  return (
    <section className="mt-8 max-w-6xl mx-auto px-4">
      {/* Contract Metadata Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 p-4 bg-base-200 rounded-lg">
        <div className="flex items-center gap-3">
          <span className="text-lg font-semibold truncate">Results for "{response.query}"</span>
          <span className={`badge ${response.parsed_intent.confidence === 'high' ? 'badge-success' : response.parsed_intent.confidence === 'medium' ? 'badge-warning' : 'badge-error'}`}>
            {response.parsed_intent.confidence} confidence
          </span>
        </div>
        <div className="text-sm text-base-content/70 font-mono">
          {response.total_matches} matches • {response.processing_time_ms?.toFixed(1)}ms
        </div>
      </div>

      {/* Results Grid */}
      {response.total_matches === 0 ? (
        <div className="text-center py-16 text-base-content/50">
          <p className="text-lg">No products matched your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {response.results.map((result) => (
            <div key={result.product.id} className="card bg-base-100 shadow-sm hover:shadow-md transition-shadow border border-base-300">
              <div className="card-body p-5">
                <div className="flex justify-between items-start">
                  <h2 className="card-title text-base leading-tight">{result.product.name}</h2>
                  <span className="text-lg font-bold text-primary">${result.product.price.toFixed(2)}</span>
                </div>
                <p className="text-sm text-base-content/60 capitalize">{result.product.category}</p>
                
                <MatchBadges signals={result.match_signals} />
                
                <div className="divider my-2"></div>
                <div className="flex justify-between items-center text-xs">
                  <span className="font-medium">Score: {(result.score * 100).toFixed(0)}%</span>
                  <span className="badge badge-sm badge-ghost">{result.product.brand || "Unbranded"}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}