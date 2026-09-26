import AgentRunPanel from "./components/AgentRunPanel";
import HealthBadge from "./components/HealthBadge";
import ProvidersPanel from "./components/ProvidersPanel";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>AI Agent Platform</h1>
          <p className="subtitle">
            Minimal demo console — talks to the existing FastAPI backend
            (<code>/health</code>, <code>/providers</code>,{" "}
            <code>/agent/run</code>).
          </p>
        </div>
        <HealthBadge />
      </header>

      <main className="app-main">
        <AgentRunPanel />
        <ProvidersPanel />
      </main>

      <footer className="app-footer">
        Vendor-agnostic agent starter · no auth · no streaming · read-only
        provider ledger
      </footer>
    </div>
  );
}
