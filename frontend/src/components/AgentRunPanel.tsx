import { useState } from "react";
import type { FormEvent } from "react";
import { ApiError, runAgent } from "../api/client";
import type { RunResponse } from "../types";
import TracePanel from "./TracePanel";

export default function AgentRunPanel() {
  const [input, setInput] = useState("What is the capital of France? Search if unsure.");
  const [maxSteps, setMaxSteps] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RunResponse | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    // Only send max_steps when the user entered a positive integer; otherwise
    // let the backend apply its own default.
    const parsed = maxSteps.trim() === "" ? null : Number(maxSteps);
    const max_steps =
      parsed != null && Number.isFinite(parsed) && parsed > 0
        ? Math.floor(parsed)
        : null;

    try {
      const data = await runAgent({ input, max_steps });
      setResult(data);
    } catch (err) {
      if (err instanceof ApiError) {
        const code = err.status === 0 ? "network error" : `HTTP ${err.status}`;
        setError(`${code}: ${err.detail ?? err.message}`);
      } else {
        setError(String(err));
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="column">
      <section className="panel">
        <h2>Agent run</h2>
        <form className="run-form" onSubmit={onSubmit}>
          <label className="field">
            <span>Input</span>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              rows={3}
              placeholder="Ask the agent something…"
              disabled={loading}
            />
          </label>

          <label className="field field--inline">
            <span>max_steps (optional)</span>
            <input
              type="number"
              min={1}
              step={1}
              value={maxSteps}
              onChange={(e) => setMaxSteps(e.target.value)}
              placeholder="backend default"
              disabled={loading}
            />
          </label>

          <button type="submit" className="run-button" disabled={loading || input.trim() === ""}>
            {loading ? "Running…" : "Run"}
          </button>
        </form>

        {loading && <p className="loading">Waiting for the agent loop to finish…</p>}

        {error && (
          <div className="error" role="alert">
            <strong>Error.</strong> {error}
          </div>
        )}

        {result && !loading && (
          <div className="result">
            <h3>Answer</h3>
            <p className="answer">{result.answer}</p>
            <dl className="result-meta">
              <div>
                <dt>Selected LLM</dt>
                {/* `llm` is absent on the "step budget exhausted" path. */}
                <dd>{result.llm ?? "—"}</dd>
              </div>
              <div>
                <dt>Total cost</dt>
                <dd>${result.cost_usd.toFixed(6)}</dd>
              </div>
            </dl>
          </div>
        )}
      </section>

      <TracePanel trace={result?.trace ?? []} />
    </div>
  );
}
