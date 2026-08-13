.PHONY: setup dev test fmt providers

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

providers:
	curl -s localhost:8000/providers | python -m json.tool
