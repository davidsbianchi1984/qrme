# Contributing to QRME

Thanks for your interest! QRME is one of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)); see
[docs/tandem.md](docs/tandem.md) for how they fit together.

## Development setup

```bash
pip install -e .[dev]      # backend + test deps
pytest                     # run the suite (offline stub provider, no API key needed)
uvicorn qrme.api:app --reload
```

For the desktop console:

```bash
cd app
npm ci
npm run dev                # renderer in the browser
npm run electron:dev       # renderer inside Electron
```

The backend runs fully offline by default — the deterministic stub provider
answers when no `ANTHROPIC_API_KEY` is set, so tests and local dev need no
network or credentials.

## Guidelines

- **Tests pass, and cover new behavior.** Run `pytest` before opening a PR;
  add tests for any new endpoint or rule. The front-end must still build
  (`cd app && npm run build`) — CI checks both.
- **Match the surrounding style.** Standard-library-first Python; keep comments
  at the density of the file you're editing.
- **Keep the products decoupled.** Cross-product calls go over HTTP at the
  client seam (see `qrme/pdi_client.py`, `qrme/cloud.py`), never direct imports
  of another product's internals.
- **Respect the data promises.** Owner/interactor tokens gate access; never log
  secrets or plaintext that belongs in the PDI vault.

## Pull requests

1. Branch off `main`.
2. Make the change with tests; keep commits focused.
3. Open a PR describing the what and why. CI runs `pytest` and the front-end
   smoke build.

By contributing you agree that your contributions are licensed under the
project's [MIT License](LICENSE).
