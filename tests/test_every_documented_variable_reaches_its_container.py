"""Every documented variable reaches its container.

PDI_RESIDENT_PULSE was the scar: the deploy page told the operator to
set it in `.env`, and `docker/beta-compose.yml` never forwarded it —
compose passes only what a service's environment block names, so the
standing tasks would have stood still on a box whose operator had done
everything the instructions said. PDI_OLLAMA_URL was the second
instance, and a second instance is when a lesson becomes a guard.

    asked     does the page's .env template match the compose file
    mattered  a documented dial that reaches no container is a lie
              with good documentation
"""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "beta-deploy.md"
COMPOSE = ROOT / "docker" / "beta-compose.yml"


def _template_vars() -> set[str]:
    """The variables §2 tells the operator to put in `.env`."""
    lines = DOC.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.strip().startswith("cat > .env"))
    out = set()
    for line in lines[start + 1:]:
        if line.strip() == "EOF":
            break
        m = re.match(r"([A-Z][A-Z0-9_]*)=", line.strip())
        if m:
            out.add(m.group(1))
    assert out, "the .env template went missing from the deploy page"
    return out


def _service_environment_refs() -> set[str]:
    """Every ${VAR} that some service's environment block actually
    forwards — the only place a value in `.env` becomes a value a
    container can see."""
    doc = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    refs: set[str] = set()
    for service in (doc.get("services") or {}).values():
        env = service.get("environment") or {}
        values = env.values() if isinstance(env, dict) else env
        for v in values:
            refs.update(re.findall(r"\$\{([A-Z][A-Z0-9_]*)", str(v)))
    return refs


def _walk_strings(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from _walk_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_strings(v)
    elif isinstance(node, str):
        yield node


def _required_refs() -> set[str]:
    """Every ${VAR:?} the compose file refuses to start without — read
    from the parsed YAML, never the raw text: a commented-out block is a
    door deliberately not built yet, not a requirement."""
    doc = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    refs: set[str] = set()
    for value in _walk_strings(doc):
        refs.update(re.findall(r"\$\{([A-Z][A-Z0-9_]*):\?", value))
    return refs


def test_every_templated_variable_reaches_a_container():
    """The forward direction — the pulse bug, made impossible to repeat.
    A variable the page documents must be forwarded by some service's
    environment block, or it is a dial connected to nothing."""
    missing = sorted(_template_vars() - _service_environment_refs())
    assert not missing, (
        "documented in the deploy page's .env template but forwarded by "
        "no service's environment block — the operator sets these and "
        "nothing changes:\n    " + "\n    ".join(missing)
        + "\n  Forward them in docker/beta-compose.yml, or strike them "
          "from the template — but a documented dial must reach a "
          "container.")


def test_every_required_variable_is_in_the_template():
    """The reverse direction: a ${VAR:?} the compose file refuses to
    start without must be a variable the page told the operator about —
    a deploy cannot demand what the instructions never mentioned."""
    undocumented = sorted(_required_refs() - _template_vars())
    assert not undocumented, (
        "required by docker/beta-compose.yml (${VAR:?}) but absent from "
        "the deploy page's .env template:\n    "
        + "\n    ".join(undocumented)
        + "\n  Document them in docs/beta-deploy.md §2, or stop "
          "requiring them.")
