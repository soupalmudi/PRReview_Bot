import { useState } from "react";

export interface ReviewRequestPayload {
  repo?: string;
  prNumber?: string;
  diff: string;
  filesChanged?: string[];
  config?: {
    model?: string;
    temperature?: number;
    maxTokens?: number;
  };
}

interface Props {
  loading: boolean;
  onSubmit: (payload: ReviewRequestPayload) => Promise<void>;
}

export function ReviewForm({ loading, onSubmit }: Props) {
  const [repo, setRepo] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [diff, setDiff] = useState("");
  const [model, setModel] = useState("gpt-4o-mini");

  const disabled = loading || !diff.trim();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await onSubmit({
      repo: repo || undefined,
      prNumber: prNumber || undefined,
      diff,
      config: { model }
    });
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="row">
        <div>
          <label>Repository (optional)</label>
          <input value={repo} onChange={(e) => setRepo(e.target.value)} placeholder="org/repo" />
        </div>
        <div>
          <label>PR Number (optional)</label>
          <input value={prNumber} onChange={(e) => setPrNumber(e.target.value)} placeholder="#42" />
        </div>
      </div>
      <div style={{ marginTop: 12 }}>
        <label>Diff</label>
        <textarea
          value={diff}
          onChange={(e) => setDiff(e.target.value)}
          placeholder="Paste git diff here..."
          required
        />
      </div>
      <div className="row" style={{ marginTop: 12 }}>
        <div>
          <label>Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="gpt-4o-mini">gpt-4o-mini</option>
            <option value="gpt-4o">gpt-4o</option>
            <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
          </select>
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "flex-end", gap: 8 }}>
          <button type="button" className="button-ghost" onClick={() => setDiff("")}>
            Clear
          </button>
          <button type="submit" className="button-primary" disabled={disabled}>
            {loading ? "Analyzing..." : "Run Review"}
          </button>
        </div>
      </div>
    </form>
  );
}
