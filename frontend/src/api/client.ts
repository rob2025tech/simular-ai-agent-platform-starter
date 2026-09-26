// Thin, typed fetch wrappers over the three existing backend endpoints.
// All paths are RELATIVE so the same code works behind the Vite dev proxy
// and when served same-origin by FastAPI's StaticFiles mount in production.

import type {
  Health,
  HttpErrorDetail,
  Providers,
  RunRequest,
  RunResponse,
} from "../types";

// A structured error carrying the HTTP status and, when present, the
// FastAPI `detail` string (e.g. the 503 "no usable provider" message).
export class ApiError extends Error {
  readonly status: number;
  readonly detail?: string;

  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

// FastAPI 422 responses put an array of validation-error objects in `detail`
// (e.g. [{loc: ["body", "input"], msg: "Field required", ...}]). Rendering
// those objects directly would crash React, so flatten them to one string.
function formatDetail(detail: HttpErrorDetail["detail"]): string | undefined {
  if (typeof detail === "string") return detail;
  if (!Array.isArray(detail) || detail.length === 0) return undefined;
  const parts = detail.map((item) => {
    if (item == null || typeof item !== "object") return String(item);
    const err = item as { loc?: unknown[]; msg?: unknown };
    const path = Array.isArray(err.loc)
      ? err.loc.map(String).filter((p) => p !== "body").join(".")
      : "";
    const msg = typeof err.msg === "string" ? err.msg : JSON.stringify(err);
    return path ? `${path}: ${msg}` : msg;
  });
  return parts.join("; ");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, init);
  } catch (err) {
    // Network failure / API unreachable (no CORS, backend down, wrong origin).
    throw new ApiError(0, `Could not reach the API at ${path}`, String(err));
  }

  if (!res.ok) {
    let detail: string | undefined;
    try {
      const body = (await res.json()) as HttpErrorDetail;
      detail = formatDetail(body.detail);
    } catch {
      // Non-JSON error body; leave detail undefined.
    }
    throw new ApiError(
      res.status,
      detail ?? `Request to ${path} failed with status ${res.status}`,
      detail,
    );
  }

  return (await res.json()) as T;
}

export function getHealth(): Promise<Health> {
  return request<Health>("/health");
}

export function getProviders(): Promise<Providers> {
  return request<Providers>("/providers");
}

export function runAgent(body: RunRequest): Promise<RunResponse> {
  return request<RunResponse>("/agent/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // Omit max_steps entirely when not provided so the backend applies its
    // own default (settings().agent_max_steps) rather than receiving null.
    body: JSON.stringify(
      body.max_steps == null
        ? { input: body.input }
        : { input: body.input, max_steps: body.max_steps },
    ),
  });
}
