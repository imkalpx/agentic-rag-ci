# Contributing

Thanks for your interest in The Intelligence Times! Bug reports, ideas and pull requests are all welcome.

## Getting set up

```bash
git clone https://github.com/imkalpx/agentic-rag-ci
cd agentic-rag-ci
bash run.sh                                  # creates .venv and .env
pip install -r requirements-dev.txt
pytest -q                                    # offline tests, no API keys needed
```

To run the full pipeline you need two free keys in `.env`: `GROQ_API_KEY` and `PINECONE_API_KEY` (see the README quickstart).

## Making a change

1. Open an issue first for anything bigger than a small fix, so we can agree on the approach.
2. Create a branch, make your change, and add or update tests in `tests/` where it makes sense.
3. Run `pytest -q` before opening a pull request. CI runs the same tests on every PR.
4. Keep PRs focused: one feature or fix per PR is much easier to review.

## Good places to start

- **New data sources** — add a `fetch_*` function in `src/ingest.py` (e.g. RSS feeds, Hacker News, SEC filings).
- **New specialist agents** — agents are defined as specs in `src/agents.py`.
- **Retrieval experiments** — tune RRF, try other re-rankers, or add an evaluation set.
- **Tests** — more offline coverage for `src/agents.py` and `app/newsprint.py`.

## Ground rules

- Never commit API keys. `.env` is gitignored; use `.env.example` for new settings.
- Be kind and constructive in issues and reviews.
