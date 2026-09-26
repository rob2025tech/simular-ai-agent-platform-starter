// Type definitions mirroring the existing backend HTTP contract exactly.
// Source of truth: app/main.py, app/router.py (report/candidates), app/agent.py.
// Nothing here invents fields the backend does not already return.

export type Capability =
  | "llm"
  | "embeddings"
  | "vector"
  | "search"
  | "storage"
  | "obs";

export type RoutingStrategy =
  | "explicit"
  | "cheapest_first"
  | "credits_first"
  | "local_first";

// GET /health -> app.main.health()
export interface Health {
  ok: boolean;
  strategy: string;
}

// One row of GET /providers "ledger" -> app.router.report()
export interface LedgerRow {
  capability: Capability;
  provider: string;
  installed: boolean;
  credentials: boolean;
  reachable: boolean;
  free: boolean;
  local: boolean;
  cost_per_1k_usd: number;
  credit_remaining_usd: number;
}

// GET /providers -> app.main.providers()
export interface Providers {
  strategy: string;
  selected: Record<string, string | null>;
  registered: Record<string, string[]>;
  ledger: LedgerRow[];
}

// POST /agent/run request body -> app.main.RunRequest
export interface RunRequest {
  input: string;
  // Optional; the backend falls back to settings().agent_max_steps when null.
  max_steps?: number | null;
}

// LLM step entry in the trace (agent.run appends: step, provider, output, cost_usd).
export interface LlmTraceEntry {
  step: number;
  provider: string;
  output: string;
  cost_usd: number;
}

// Search/tool step entry (agent.run appends: step, tool, provider, query, hits).
export interface SearchTraceEntry {
  step: number;
  tool: string;
  provider: string;
  query: string;
  hits: number;
}

// The backend emits heterogeneous trace entries; render defensively.
export type TraceEntry = Partial<LlmTraceEntry & SearchTraceEntry> & {
  step?: number;
};

// POST /agent/run response -> agent.run() return value.
// NOTE: "llm" is absent on the "step budget exhausted" path, so it is optional.
export interface RunResponse {
  answer: string;
  cost_usd: number;
  llm?: string;
  trace: TraceEntry[];
}

// FastAPI HTTPException envelope. `detail` is a string for HTTPException
// (e.g. the 503 "no usable provider" case), but an array of validation-error
// objects for 422 request-validation failures — normalize before rendering.
export interface HttpErrorDetail {
  detail?: string | unknown[];
}
