# simular-ai-agent-platform-starter

A vendor-agnostic AI agent platform skeleton. Every external dependency sits behind a
small interface, so you can **swap vendors with one line of config** — and a
cost-aware router will automatically prefer **free / local / credit-funded** providers.

## Why

Agent stacks get locked to one vendor fast. Here every capability is a *port*:

| Capability | Free / local option | Credit-friendly options |
|---|---|---|
| LLM | `ollama` (local), `groq` (free tier), `gemini` (free tier) | `openai`, `anthropic`, `openrouter`, `together` |
| Embeddings | `fastembed` (local, ONNX) | `openai`, `gemini`, `voyage` |
| Vector store | `chroma` (local file), `sqlite-vec` | `qdrant`, `pgvector` |
| Web search | `duckduckgo` (no key) | `tavily`, `brave`, `serper` |
| Storage | `sqlite` (local file) | `postgres`, `supabase` |
| Observability | `console`, `noop` | `langfuse`, `otel` |

## Quickstart (zero cost, zero API keys)

```bash
make setup            # venv + deps
ollama pull llama3.2  # optional; otherwise set LLM_PROVIDER=echo
cp .env.example .env
make dev              # http://localhost:8000/docs
```

```bash
curl -s localhost:8000/agent/run -H 'content-type: application/json' \
  -d '{"input":"What is the capital of France? Search if unsure."}' | jq
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

```
app/
  main.py          FastAPI surface (/agent/run, /providers, /health)
  settings.py      env-driven config
  registry.py      provider registry + auto-discovery
  router.py        cost-aware selection & failover
  agent.py         minimal tool-using agent loop
  providers/       one folder per capability
config/providers.yaml
tests/
```

## Licence

MIT
# simular-ai-agent-platform-starter
