"""Entry point for the PyInstaller-bundled QRME backend.

The desktop installer ships two halves: the Electron studio console, and
this — the whole Python backend frozen into one executable
(``qrme-backend`` / ``qrme-backend.exe``) that the Electron main process
spawns at launch when no backend is already answering. That is what makes
the installer double-click-and-done: no Python on the machine, no terminal,
no env vars.

Defaults are chosen for that launch and only that launch:

* **CORS open** — the console calls from its own origin; without this every
  request dies as "Failed to fetch". Same posture as ``python -m qrme serve``.
* **Loopback only** — the spawned backend binds 127.0.0.1 and is not
  reachable from the network. (Run ``python -m qrme phone`` for that, on
  purpose.)
* **Data under the app's user-data directory** — Electron passes ``QRME_DB``;
  an unset one falls back to the platform's per-user app-data location, so a
  double-clicked backend never scatters ``qrme.db`` into whatever directory
  it started in.

Everything is still overridable through the same environment variables the
unbundled backend reads.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _default_db() -> str:
    if os.environ.get("QRME_DB"):
        return os.environ["QRME_DB"]
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME",
                                   Path.home() / ".local" / "share"))
    directory = base / "QRME"
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory / "qrme.db")


def main() -> None:
    # The frozen Windows backend inherits a cp1252 stdout; any print of a
    # character outside it would raise mid-request. Replace, never raise.
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    os.environ.setdefault("QRME_CORS_ORIGINS", "*")
    os.environ["QRME_DB"] = _default_db()
    port = int(os.environ.get("QRME_PORT", "8000"))

    import uvicorn

    from qrme.api import create_app

    print(f"QRME backend — http://127.0.0.1:{port} "
          f"(db: {os.environ['QRME_DB']})", flush=True)
    uvicorn.run(create_app(), host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
