import { useCallback, useEffect, useState } from "react";
import { ApiError, getProviders } from "../api/client";
import type { Providers } from "../types";

const CAPABILITIES = [
  "llm",
  "embeddings",
  "vector",
  "search",
  "storage",
  "obs",
] as const;

export default function ProvidersPanel() {
  const [data, setData] = useState<Providers | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getProviders());
    } catch (err) {
      setData(null);
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Providers</h2>
        <button type="button" onClick={() => void load()} disabled={loading}>
          {loading ? "Loading…" : "Reload"}
        </button>
      </div>

      {error && (
        <div className="error" role="alert">
          <strong>Error.</strong> {error}
        </div>
      )}

      {data && (
        <>
          <p className="strategy">
            Routing strategy: <code>{data.strategy}</code>
          </p>

          <h3>Selected</h3>
          <ul className="selected">
            {CAPABILITIES.map((cap) => (
              <li key={cap}>
                <span className="cap">{cap}</span>
                <span className="pick">{data.selected?.[cap] ?? "—"}</span>
              </li>
            ))}
          </ul>

          <h3>Ledger</h3>
          <div className="table-wrap">
            <table className="ledger">
              <thead>
                <tr>
                  <th>capability</th>
                  <th>provider</th>
                  <th>installed</th>
                  <th>credentials</th>
                  <th>reachable</th>
                  <th>free</th>
                  <th>local</th>
                  <th>cost / 1k</th>
                  <th>credit</th>
                </tr>
              </thead>
              <tbody>
                {data.ledger.map((row, i) => (
                  <tr key={`${row.capability}-${row.provider}-${i}`}>
                    <td>{row.capability}</td>
                    <td className="provider-name">{row.provider}</td>
                    <td>
                      <Flag on={row.installed} />
                    </td>
                    <td>
                      <Flag on={row.credentials} />
                    </td>
                    <td>
                      <Flag on={row.reachable} />
                    </td>
                    <td>
                      <Flag on={row.free} />
                    </td>
                    <td>
                      <Flag on={row.local} />
                    </td>
                    <td className="num">${row.cost_per_1k_usd.toFixed(4)}</td>
                    <td className="num">${row.credit_remaining_usd.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}

function Flag({ on }: { on: boolean }) {
  return <span className={`flag ${on ? "flag--on" : "flag--off"}`}>{on ? "yes" : "no"}</span>;
}
