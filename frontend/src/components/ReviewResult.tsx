import { useMemo, useState } from "react";

export type FindingView = {
  id: string;
  severity: "critical" | "major" | "minor" | "nit";
  category: string;
  filePath?: string;
  line?: number;
  message: string;
  suggestion?: string;
};

interface Props {
  findings: FindingView[];
  loading: boolean;
}

export function ReviewResult({ findings, loading }: Props) {
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  const filtered = useMemo(() => {
    if (severityFilter === "all") return findings;
    return findings.filter((f) => f.severity === severityFilter);
  }, [findings, severityFilter]);

  return (
    <div>
      <div className="grid-2" style={{ marginBottom: 12 }}>
        <div className="muted">LLM findings grouped by severity and category.</div>
        <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
          <option value="all">All severities</option>
          <option value="critical">Critical</option>
          <option value="major">Major</option>
          <option value="minor">Minor</option>
          <option value="nit">Nit</option>
        </select>
      </div>
      {loading ? <div className="muted">Analyzing diff...</div> : null}
      {!loading && filtered.length === 0 ? <div className="muted">No findings yet.</div> : null}
      <div className="findings">
        {filtered.map((finding) => (
          <FindingCard key={finding.id} finding={finding} />
        ))}
      </div>
    </div>
  );
}

function FindingCard({ finding }: { finding: FindingView }) {
  const severityClass = `chip-sev-${finding.severity}`;

  return (
    <div className="finding">
      <div className="finding-header">
        <div className="meta">
          <span className={`chip ${severityClass}`}>{finding.severity}</span>
          <span className="chip chip-category">{finding.category}</span>
          {finding.filePath ? (
            <span className="muted">
              {finding.filePath}
              {finding.line ? `:${finding.line}` : ""}
            </span>
          ) : null}
        </div>
      </div>
      <div style={{ marginTop: 8 }}>{finding.message}</div>
      {finding.suggestion ? (
        <div className="muted" style={{ marginTop: 6 }}>
          Suggestion: {finding.suggestion}
        </div>
      ) : null}
    </div>
  );
}
