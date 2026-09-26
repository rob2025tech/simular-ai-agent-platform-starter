import type { TraceEntry } from "../types";

// Renders the backend `trace` array exactly as produced by agent.run().
// Entries are heterogeneous: an LLM step has {provider, output, cost_usd};
// a search/tool step has {tool, provider, query, hits}. We branch on the
// presence of `tool`/`query` and only render fields that actually exist —
// no data is invented.
export default function TracePanel({ trace }: { trace: TraceEntry[] }) {
  if (!trace || trace.length === 0) {
    return (
      <section className="panel">
        <h2>Execution trace</h2>
        <p className="empty">No trace yet — run the agent to see steps.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2>Execution trace</h2>
      <ol className="trace">
        {trace.map((entry, i) => {
          const isTool = entry.tool != null || entry.query != null;
          return (
            <li
              key={i}
              className={`trace-item ${isTool ? "trace-item--tool" : "trace-item--llm"}`}
            >
              <div className="trace-head">
                <span className="trace-kind">
                  {isTool ? `tool · ${entry.tool ?? "search"}` : "llm"}
                </span>
                {entry.step != null && (
                  <span className="trace-step">step {entry.step}</span>
                )}
                {entry.provider != null && (
                  <span className="trace-provider">provider: {entry.provider}</span>
                )}
              </div>

              <dl className="trace-fields">
                {entry.query != null && (
                  <Field label="query" value={entry.query} />
                )}
                {entry.hits != null && (
                  <Field label="hits" value={String(entry.hits)} />
                )}
                {entry.cost_usd != null && (
                  <Field label="cost_usd" value={String(entry.cost_usd)} />
                )}
              </dl>

              {entry.output != null && (
                <pre className="trace-output">{entry.output}</pre>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="trace-field">
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}
