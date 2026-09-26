import { useCallback, useEffect, useState } from "react";
import { ApiError, getHealth } from "../api/client";
import type { Health } from "../types";

type Status = "loading" | "up" | "down";

export default function HealthBadge() {
  const [status, setStatus] = useState<Status>("loading");
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setStatus("loading");
    setError(null);
    try {
      const data = await getHealth();
      setHealth(data);
      setStatus(data.ok ? "up" : "down");
    } catch (err) {
      setHealth(null);
      setStatus("down");
      setError(err instanceof ApiError ? err.message : String(err));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const label =
    status === "loading"
      ? "Checking API…"
      : status === "up"
        ? `API reachable · strategy: ${health?.strategy ?? "unknown"}`
        : "API unreachable";

  return (
    <div className={`health health--${status}`} title={error ?? undefined}>
      <span className="health-dot" aria-hidden="true" />
      <span className="health-label">{label}</span>
      <button
        type="button"
        className="health-refresh"
        onClick={() => void refresh()}
      >
        Refresh
      </button>
    </div>
  );
}
