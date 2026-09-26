# simular-ai-agent-platform-starter

A vendor-agnostic AI agent platform skeleton with a small React browser console. Every external dependency sits behind a small interface, so you can **swap vendors with one line of config** — and a cost-aware router will automatically prefer **free / local / credit-funded** providers.

## Why

Agent stacks get locked to one vendor fast. Here every capability is a *port*:

| Capability    | Free / local option                                        | Credit-friendly options                         |
| ------------- | ---------------------------------------------------------- | ----------------------------------------------- |
| LLM           | `ollama` (local), `groq` (free tier), `gemini` (free tier) | `openai`, `anthropic`, `openrouter`, `together` |
| Embeddings    | `fastembed` (local, ONNX)                                  | `openai`, `gemini`, `voyage`                    |
| Vector store  | `chroma` (local file), `sqlite-vec`                        | `qdrant`, `pgvector`                            |
| Web search    | `duckduckgo` (no key)                                      | `tavily`, `brave`, `serper`                     |
| Storage       | `sqlite` (local file)                                      | `postgres`, `supabase`                          |
| Observability | `console`, `noop`                                          | `langfuse`, `otel`                              |

## Quickstart (zero cost, zero API keys)

```bash
make setup
cp .env.example .env
make dev
```

With the backend running, the FastAPI API is available at:

* Browser console: `http://localhost:8000/`
* API documentation: `http://localhost:8000/docs`

The browser console displays:

* Agent input and optional step limit
* Agent answer, selected LLM, and cost
* Execution trace
* Provider routing strategy and selected providers
* Provider capability/credential/reachability ledger
* Backend health

The provider strategy and ledger are currently **read-only in the browser console**. Routing remains controlled by the existing backend configuration.

### Frontend development mode

For frontend development with Vite's development server:

**Terminal 1 — FastAPI**

```bash
make dev
```

**Terminal 2 — React/Vite**

```bash
cd frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

The Vite development server proxies `/health`, `/providers`, and `/agent/run` to the FastAPI backend.

### Same-origin frontend

To serve the built React frontend directly from FastAPI:

```bash
cd frontend
npm install
npm run build
cd ..
make dev
```

Then open:

```text
http://localhost:8000/
```

The backend serves `frontend/dist` only when that directory exists. The API and FastAPI documentation remain available at `/health`, `/providers`, `/agent/run`, and `/docs`.

## API

The existing API can also be used directly without the browser console:

```bash
curl -s localhost:8000/agent/run -H 'content-type: application/json' \
  -d '{"input":"What is the capital of France? Search if unsure."}' | jq
```

Health:

```bash
curl -s localhost:8000/health | jq
```

Provider ledger:

```bash
curl -s localhost:8000/providers | jq
```

## Swapping a vendor

Config-first — nothing else changes:

```bash
LLM_PROVIDER=groq        # was: ollama
SEARCH_PROVIDER=tavily   # was: duckduckgo
```

Or let the router decide. `config/providers.yaml` declares, per provider,
its `cost_per_1k`, whether it is `free`, and any `credits` you hold.
`ROUTING_STRATEGY=cheapest_first` walks that list, skipping providers whose
credentials are missing and failing over on error.

## Tracking free credits

```yaml
llm:
  - name: anthropic
    credits: { remaining_usd: 250, expires: 2026-12-31 }
```

`GET /providers` reports what is configured, reachable, and what credit remains, so
you can burn expiring credits before paying cash. Set `ROUTING_STRATEGY=credits_first`
to prefer providers with unexpired credits over free-but-rate-limited ones.

## Adding a vendor

1. Drop a file in `app/providers/<capability>/`.
2. Implement the port from `app/providers/base.py`.
3. Decorate with `@register("<capability>", "<name>")`.
4. Add a cost entry in `config/providers.yaml`.

No core code changes — discovery is automatic.

## Layout

```text
app/
  main.py          FastAPI surface (/agent/run, /providers, /health)
  settings.py      env-driven config
  registry.py      provider registry + auto-discovery
  router.py        cost-aware selection & failover
  agent.py         minimal tool-using agent loop
  providers/       one folder per capability

frontend/
  src/
    App.tsx
    api/            FastAPI client
    components/     agent, trace, provider, health panels
    styles.css
  vite.config.ts
  package.json

config/providers.yaml
tests/
```

## Licence

MIT
