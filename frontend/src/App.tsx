import { useState } from "react";
import { ReviewForm, ReviewRequestPayload } from "./components/ReviewForm";
import { ReviewResult, FindingView } from "./components/ReviewResult";

export default function App() {
  const [findings, setFindings] = useState<FindingView[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(payload: ReviewRequestPayload) {
    setLoading(true);
    setError(null);
    setFindings([]);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE ?? "http://localhost:5001"}/api/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
      setFindings(data.findings || []);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to fetch review");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <div>
          <div className="pill">LLM-powered PR reviewer</div>
          <h1>Automated Review Bot</h1>
        </div>
        <div className="muted">Paste a diff, get findings in seconds.</div>
      </header>
      <main>
        <div className="card">
          <h2>Submit Review</h2>
          <ReviewForm onSubmit={handleSubmit} loading={loading} />
          {error ? <div className="muted" style={{ color: "#ff6b6b", marginTop: 8 }}>Error: {error}</div> : null}
        </div>
        <div className="card">
          <h2>Findings</h2>
          <ReviewResult findings={findings} loading={loading} />
        </div>
      </main>
    </div>
  );
}
