"""The container image's contract with the code that runs inside it.

These are static checks on the Dockerfile, not a build — CI has no Docker
daemon. They exist because the ways this image can be wrong are quiet ones:
the studio silently not served, the database written into a layer that the
next deploy discards. Both are invisible until a user hits them, and both are
a mismatch between two files that nothing else keeps in step.
"""

import re
from pathlib import Path

import yaml

from qrme import mobile

ROOT = Path(__file__).resolve().parent.parent
DOCKERFILE = (ROOT / "Dockerfile").read_text()
COMPOSE = (ROOT / "docker" / "docker-compose.yml").read_text()


def _env(name: str) -> str | None:
    """The value the Dockerfile's ENV instructions give ``name``."""
    m = re.search(rf"^\s*{name}=(\S+)", DOCKERFILE, re.MULTILINE)
    return m.group(1) if m else None


def test_console_dir_points_at_where_the_build_is_copied():
    """The regression this file was written for.

    ``console_dir`` resolves ``app/dist`` relative to the *package*, and after
    ``pip install`` the package lives in site-packages — nowhere near the dist
    the image copies to /srv. Only the explicit override makes the two agree,
    so the image must set it, and to exactly the COPY destination.
    """
    assert _env("QRME_CONSOLE_DIR") == "/srv/app/dist"
    assert re.search(r"COPY --from=studio /src/app/dist \./app/dist", DOCKERFILE)
    assert "WORKDIR /srv" in DOCKERFILE


def test_console_dir_honours_the_override(tmp_path, monkeypatch):
    """And that the override is load-bearing in the code, not just the image."""
    dist = tmp_path / "dist"
    dist.mkdir()
    monkeypatch.setenv("QRME_CONSOLE_DIR", str(dist))
    assert mobile.console_dir() is None          # nothing built there yet
    (dist / "index.html").write_text("<!doctype html>")
    assert mobile.console_dir() == dist


def test_database_lives_on_a_mounted_volume():
    """A container restart must not be a data-loss event: the default DB path
    has to sit under the declared volume."""
    db = _env("QRME_DB")
    assert db == "/data/qrme.db"
    assert 'VOLUME ["/data"]' in DOCKERFILE


def test_service_does_not_run_as_root():
    assert re.search(r"^USER qrme", DOCKERFILE, re.MULTILINE)
    assert DOCKERFILE.index("USER qrme") < DOCKERFILE.index("CMD ")


def test_listens_on_all_interfaces_and_honours_platform_port():
    """Binding to localhost inside a container publishes nothing; and hosts
    that assign a port need it honoured or the health check never passes."""
    cmd = DOCKERFILE[DOCKERFILE.index("CMD ["):]
    assert "--host 0.0.0.0" in cmd
    assert "${PORT:-8000}" in cmd


def test_suite_harness_gives_pdi_an_admin_token():
    """PDI's dev-open admin mode is open only to callers on the same machine.
    Every service here reaches it over the compose network, where it fails
    closed — so the harness has to configure a token and both drivers have to
    present it. Leaving any one of the three out fails the whole run at
    tenant creation, which is the first thing it does.
    """
    services = yaml.safe_load(COMPOSE)["services"]
    for name in ("pdi", "bootstrap", "e2e"):
        assert "PDI_ADMIN_TOKEN" in services[name]["environment"], name
    # One anchor, so the token PDI requires and the token the drivers send
    # cannot drift apart.
    assert (services["pdi"]["environment"]["PDI_ADMIN_TOKEN"]
            == services["bootstrap"]["environment"]["PDI_ADMIN_TOKEN"]
            == services["e2e"]["environment"]["PDI_ADMIN_TOKEN"])
    for driver in ("bootstrap.py", "e2e.py"):
        source = (ROOT / "docker" / driver).read_text()
        assert 'os.environ.get("PDI_ADMIN_TOKEN"' in source
        assert "Bearer" in source or "token=PDI_ADMIN" in source
