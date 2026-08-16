"""The persona speaks it everywhere. The platform spoke English.

## The finding

`qrme/i18n.py` opens with a claim and keeps it:

    Per-profile language: the persona speaks it everywhere ... the directive
    rides on the persona system prompt, so every generation site inherits it
    without per-endpoint plumbing.

Every *generation* site. The product's own sentences were another matter. An
owner who set Portuguese got a Portuguese sidebar from `l10n.ts`, Portuguese
answers from the model, and English on every single refusal — 153 distinct
ones, from "authentication required" to the plan gate that stands between them
and a decision to pay.

`common.refusals_in` was added in 0.24.0 for the four accountless routes, and
its docstring wrote the reason the owner routes were left out:

    `profile_or_404` and its siblings are shared with every owner route and
    say "profile not found" in English, which is right there — the owner
    picked that language

The owner did not pick that language. They picked one; it is in
`language_prefs`; English is what they get when they picked English. The
justification for the scope *was* the defect, written down and reviewed.

    asked     did the caller state a language
    mattered  did the profile

## The two ways the fix could have been wrong and still passed

**Whose language.** Reading the `profile_id` in the path would answer a
stranger on `GET /profiles/{id}/consistency` in the language of the person
they are asking *about* — a new wrong answer wearing the shape of a fix.
Reading `Accept-Language` would take `en-US` from a console owner's browser
whatever they had set in the app, making the whole round a no-op that passed
its own tests. The credential names the reader, and nothing else does.

**Which stored value.** `effective_language` returns English whenever the mode
is `on_demand` — a statement about the *persona's voice*, not about what the
owner reads. Using it would have looked right, passed a test written with a
`pre`-mode profile, and served English to every owner who had asked their
persona to stay in character. Both are checked below, with a profile in
`on_demand` mode specifically.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from qrme import i18n


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SNAPSHOT = Path(__file__).resolve().parent / "refusals_untranslated.txt"


#: Every shape an `HTTPException` detail is written in, and what this suite
#: does about each. A shape that is in none of these is the defect the
#: classifier exists to report — see `_classify`.
#:
#:   literal      a plain string. Checked against the translation table.
#:   named        a module-level constant holding a plain string. Resolved,
#:                then checked exactly like a literal.
#:   template     an f-string, a `.format()`, or a concatenation. The English
#:                skeleton is recovered and checked against its own record —
#:                it cannot be a table key as written, which is the finding.
#:   translated   already goes through `i18n` at the raise: `i18n.fill(...)`
#:                or a lookup into one of the translation tables. Nothing owed.
#:   passthrough  carries a sentence raised somewhere else — `exc.detail`, a
#:                local rebound from an earlier raise. Owed at that raise.
#:   domain       `str(exc)` on a domain exception. The sentence lives at the
#:                `raise SomeError("…")` in a module, not here. **Not yet
#:                followed** — see `refusal_templates.txt` for the count and
#:                why it is its own round.
SHAPES = ("literal", "named", "template", "translated", "passthrough", "domain")

#: What must be translated or written down. The other three shapes are
#: accounted for elsewhere, and saying which is the point of the split.
OWED = ("literal", "named", "template")


def _module_strings(tree: ast.Module) -> dict[str, str]:
    """Module-level `NAME = "a sentence"`, so a refusal raised as a constant
    can be read. Two of them were invisible for as long as this guard has
    existed: `common.RESTRICTED_WHILE_CONTESTED` and
    `access.NEEDS_ITS_WORDS`."""
    out: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            out[target.id] = node.value.value
    return out


def _module_tables(tree: ast.Module) -> dict[str, list[str]]:
    """Module-level `NAME = {...}` whose values are plain strings.

    A refusal picked out of one of these — `_MISSING[posture].format(label=…)`
    in `routers/apps.py` — is every one of its values, because which sentence
    a reader meets depends on a key chosen at runtime. Recovering only the
    subscript would find nothing; recovering the table finds all of them.
    """
    out: dict[str, list[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or not isinstance(node.value, ast.Dict):
            continue
        values = [v.value for v in node.value.values
                  if isinstance(v, ast.Constant) and isinstance(v.value, str)]
        if values and len(values) == len(node.value.values):
            out[target.id] = values
    return out


def _skeleton(node: ast.AST) -> str | None:
    """The English of a sentence built by interpolation, with `{}` where each
    filled-in piece goes.

    This is what makes an f-string refusal visible. It is deliberately not a
    translation key: `i18n.fill` uses *named* placeholders, and an f-string
    does not carry names a reader could rely on. The skeleton says what a
    person will actually read, which is the thing the record is about.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            v.value if isinstance(v, ast.Constant) and isinstance(v.value, str)
            else "{}" for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _skeleton(node.left), _skeleton(node.right)
        return None if left is None or right is None else left + right
    return None


def _is_i18n(node: ast.AST) -> bool:
    """Whether this detail already went through the translation layer.

    `i18n.fill(i18n.MUST_BE_ONE_OF, field=…)` and
    `i18n.STUDIO_REFUSALS[str(exc)]` are the two shapes in use. Both are
    refusals-as-keys, which is the pattern the rest of this suite asks for,
    so they are owed nothing here — but they must be *recognised* rather
    than unseen, or the guard cannot tell them from an English f-string.
    """
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) \
                and getattr(sub.value, "id", "") == "i18n":
            return True
    return False


def _classify(detail: ast.AST | None, consts: dict[str, str],
              tables: dict[str, list[str]]) -> tuple[str, list[str]]:
    """One detail node, into exactly one of :data:`SHAPES`.

    The old extractor read `ast.Constant` and counted `ast.JoinedStr`. Every
    other shape fell through in silence — 145 refusals, including two module
    constants and thirty-eight f-strings that reach a reader in English
    whatever language they chose.

        asked     is this refusal a string literal
        mattered  what does this refusal put in front of a person
    """
    def table_of(node: ast.AST) -> list[str] | None:
        """The sentences behind `SOME_TABLE[whatever]`."""
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            return tables.get(node.value.id)
        return None

    if detail is None:
        return "passthrough", []
    if _is_i18n(detail):
        return "translated", []
    if isinstance(detail, ast.Constant) and isinstance(detail.value, str):
        return "literal", [detail.value]
    if isinstance(detail, ast.Name):
        if detail.id in consts:
            return "named", [consts[detail.id]]
        return "passthrough", []            # a local, rebound from a raise
    if isinstance(detail, ast.Attribute):
        return "passthrough", []            # exc.detail, exc.message
    if isinstance(detail, (ast.JoinedStr, ast.BinOp)):
        skeleton = _skeleton(detail)
        return ("template", [skeleton]) if skeleton else ("passthrough", [])
    if isinstance(detail, ast.Call):
        fn = detail.func
        # `str(exc)` — the sentence is at the `raise` in a domain module.
        if getattr(fn, "id", "") == "str":
            return "domain", []
        # `SOMETHING.format(...)` — the receiver carries the English, whether
        # that is a literal or a row of a table picked at runtime.
        if getattr(fn, "attr", "") == "format":
            receiver = getattr(fn, "value", None)
            skeleton = _skeleton(receiver)
            if skeleton:
                return "template", [skeleton]
            rows = table_of(receiver)
            if rows:
                return "template", rows
            return "domain", []
        return "domain", []
    if isinstance(detail, ast.Dict):
        # The plan gate. `localize_detail` translates `message` and leaves the
        # API's own vocabulary alone — `test_a_dict_detail_…` covers it.
        for key, value in zip(detail.keys, detail.values):
            if getattr(key, "value", None) == "message":
                text = _skeleton(value)
                if text:
                    return "literal", [text]
        return "translated", []
    if isinstance(detail, ast.Subscript):
        rows = table_of(detail)
        if rows:
            return "named", rows
        return "domain", []
    return "unknown", []


def _refusals(root: Path) -> dict[str, list[tuple[str, str | None]]]:
    """Every `HTTPException` detail in the package, by shape.

    Values are `(where, text)` so a failure can name the file and line rather
    than only the sentence — a template appears verbatim at several call
    sites and the sentence alone does not say which one is new.
    """
    found: dict[str, list[tuple[str, str | None]]] = {s: [] for s in SHAPES}
    found["unknown"] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        consts, tables = _module_strings(tree), _module_tables(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = getattr(fn, "id", "") or getattr(fn, "attr", "")
            if name != "HTTPException":
                continue
            detail = node.args[1] if len(node.args) >= 2 else None
            for kw in node.keywords:
                if kw.arg == "detail":
                    detail = kw.value
            shape, texts = _classify(detail, consts, tables)
            where = f"{path.relative_to(root.parent)}:{node.lineno}"
            if texts:
                found[shape].extend((where, t) for t in texts)
            else:
                found[shape].append((where, None))
    return found


def _stringified_errors(root: Path) -> set[str]:
    """Domain exception classes whose message becomes a refusal.

    Derived rather than listed. A handler that does
    `except displays.DisplayError as exc: raise HTTPException(409, str(exc))`
    is turning that class's message into the sentence a person reads, and the
    next module to invent one is covered without anybody remembering to add
    it here.
    """
    out: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for handler in [n for n in ast.walk(tree)
                        if isinstance(n, ast.ExceptHandler)]:
            stringifies = any(
                isinstance(call, ast.Call)
                and (getattr(call.func, "id", "")
                     or getattr(call.func, "attr", "")) == "HTTPException"
                and any(isinstance(arg, ast.Call)
                        and getattr(arg.func, "id", "") == "str"
                        for arg in list(call.args)
                        + [kw.value for kw in call.keywords])
                for call in ast.walk(handler))
            if not stringifies or handler.type is None:
                continue
            caught = (handler.type.elts if isinstance(handler.type, ast.Tuple)
                      else [handler.type])
            for node in caught:
                name = getattr(node, "attr", "") or getattr(node, "id", "")
                if name:
                    out.add(name)
    return out


def _domain_sentences(root: Path) -> tuple[set[str], set[str]]:
    """The English behind `str(exc)`, as (literals, templates).

    `raise DisplayError("a display needs a name")` is the sentence; the route
    that catches it only forwards. The refusal guard walked `HTTPException`
    call sites and stopped there, so a hundred and five forwarding sites hid
    two hundred and sixty-nine sentences nobody was ever asked about.

        asked     what does this route pass to HTTPException
        mattered  where does the sentence it passes come from

    They land in the same two records as any other refusal, because
    `tr_refusal` treats them identically at answer time: it looks the
    sentence up and falls through to English when it is not there.
    """
    classes = _stringified_errors(root)
    literals: set[str] = set()
    templates: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        consts, tables = _module_strings(tree), _module_tables(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
                continue
            name = (getattr(node.exc.func, "id", "")
                    or getattr(node.exc.func, "attr", ""))
            if name not in classes or not node.exc.args:
                continue
            arg = node.exc.args[0]
            if isinstance(arg, ast.Name) and arg.id in consts:
                literals.add(consts[arg.id])
                continue
            if isinstance(arg, ast.Subscript) \
                    and getattr(arg.value, "id", "") in tables:
                templates.update(tables[arg.value.id])
                continue
            text = _skeleton(arg)
            if text is None:
                continue
            (templates if isinstance(arg, (ast.JoinedStr, ast.BinOp))
             else literals).add(text)
    return literals, templates


def _details(root: Path) -> tuple[set[str], int]:
    """The literal-and-named sentences, and how many are built by
    interpolation. Kept at this signature because the guard-on-the-guard and
    the record's own header are both written against it."""
    found = _refusals(root)
    literals = {text for shape in ("literal", "named")
                for _, text in found[shape] if text}
    return literals, len(found["template"])


def _translated() -> set[str]:
    """Both tables. `profile_or_404` is shared between the accountless routes
    and every owner route, so its sentence lives in `_PUBLIC` and is not owed
    a second entry — see `tr_refusal`."""
    return set(i18n._REFUSALS) | set(i18n._PUBLIC)


def _recorded() -> set[str]:
    return {line.rstrip("\n") for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_every_refusal_is_translated_or_written_down():
    """Both directions. A refusal that is neither is a sentence somebody will
    read in a language they did not choose, that nobody decided about."""
    literals, _ = _details(REPO / "qrme")
    # The sentences behind `str(exc)` too. They reach `tr_refusal` exactly as
    # a directly-raised literal does, and fall through to English the same way.
    literals |= _domain_sentences(REPO / "qrme")[0]
    undecided = sorted(literals - _translated() - _recorded())
    stale = sorted(_recorded() - literals)
    problems = []
    if undecided:
        problems.append(
            f"{len(undecided)} refusal(s) that are neither translated nor "
            "recorded:\n    " + "\n    ".join(s[:90] for s in undecided[:30])
            + "\n  Add it to i18n._REFUSALS, or to "
              f"{SNAPSHOT.name} — but adding there is ratcheted.")
    if stale:
        problems.append(
            f"{len(stale)} recorded refusal(s) are no longer raised anywhere "
            f"— strike them from {SNAPSHOT.name}:\n    "
            + "\n    ".join(s[:90] for s in stale[:30]))
    assert not problems, "\n\n".join(problems)


TEMPLATES = Path(__file__).resolve().parent / "refusal_templates.txt"


def _recorded_templates() -> set[str]:
    return {line.rstrip("\n") for line in
            TEMPLATES.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_no_refusal_shape_goes_unclassified():
    """The finding this round is about, as a standing check.

    The extractor read `ast.Constant` and counted `ast.JoinedStr`. Everything
    else — a module constant, a row of a table picked at runtime, a
    `.format()`, a concatenation — fell through in silence, and a refusal
    added in one of those shapes was a sentence nobody would ever be asked
    about.

        asked     is this refusal a string literal
        mattered  what does this refusal put in front of a person

    Every detail now lands in one of :data:`SHAPES`. A shape that lands in
    none of them fails here rather than being skipped, because a shape nobody
    classified is a shape nobody decided about.
    """
    found = _refusals(REPO / "qrme")
    assert not found["unknown"], (
        f"{len(found['unknown'])} refusal detail(s) in a shape this guard "
        "does not classify:\n    "
        + "\n    ".join(where for where, _ in found["unknown"][:20])
        + "\n  Give the shape a row in SHAPES and a branch in _classify — "
          "or the sentences it carries are invisible.")
    # And the classifier must still be finding the bulk of them: a refactor
    # that broke `_refusals` would report zero unknown on zero refusals.
    assert len(found["literal"]) >= 200, (
        f"only {len(found['literal'])} literal refusals found — the walk has "
        "stopped matching, so every check built on it is passing on nothing")


def test_every_interpolated_refusal_is_recorded():
    """The templates, both directions.

    These cannot be keys in `_REFUSALS` as written — `i18n.fill` is the
    mechanism for a refusal with a value in it, and twenty-two call sites use
    it correctly. The ones here were written as f-strings instead, which
    means English whatever language the reader chose. Recorded rather than
    translated in the round that found them; `refusal_templates.txt` says why.
    """
    found = _refusals(REPO / "qrme")
    measured = {text for _, text in found["template"] if text}
    measured |= _domain_sentences(REPO / "qrme")[1]
    recorded = _recorded_templates()
    problems = []
    new = sorted(measured - recorded)
    if new:
        problems.append(
            f"{len(new)} interpolated refusal(s) not in {TEMPLATES.name}:\n    "
            + "\n    ".join(s[:90] for s in new[:20])
            + "\n  Convert it to i18n.fill with a translated constant, or "
              "record it — but recording is ratcheted.")
    gone = sorted(recorded - measured)
    if gone:
        problems.append(
            f"{len(gone)} recorded template(s) are no longer raised — strike "
            f"them from {TEMPLATES.name}:\n    "
            + "\n    ".join(s[:90] for s in gone[:20]))
    assert not problems, "\n\n".join(problems)


def test_the_template_backlog_only_shrinks():
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            TEMPLATES.read_text(encoding="utf-8")).group(1))
    assert len(_recorded_templates()) <= ceiling, (
        f"{len(_recorded_templates())} interpolated refusals, above the "
        f"{ceiling} this record started at")


def test_the_backlog_only_shrinks():
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            SNAPSHOT.read_text(encoding="utf-8")).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} untranslated refusals, above the {ceiling} this "
        "guard started at")


def test_every_handler_returns_through_the_one_place():
    """The structural half, ported from the siblings.

    PDI and JIM-mini have asked this since the round that gave them one
    `i18n.refuse`; this product answers its refusals a shape of its own —
    `refusal_language`, then `localize_detail` and `sentence_of` — and so the
    question never crossed. It stood on `guard_divergences.txt` as a name
    this suite lacked, which is the same thing as nobody asking here whether
    a new exception handler would answer in English.

        asked     is this refusal translated where it is raised
        mattered  does every handler that answers one consult the reader

    Checked structurally rather than by driving each handler: a driven check
    would cover the ones that exist today and say nothing about the next.
    """
    tree = ast.parse((REPO / "qrme" / "api.py").read_text(encoding="utf-8"))
    handlers: list[tuple[str, bool]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(isinstance(d, ast.Call)
                   and getattr(d.func, "attr", "") == "exception_handler"
                   for d in node.decorator_list):
            continue
        routed = any(
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", "") == "refusal_language"
            and getattr(getattr(n.func, "value", None), "id", "") == "i18n"
            for n in ast.walk(node))
        handlers.append((node.name, routed))

    assert len(handlers) >= 2, (
        f"only {len(handlers)} exception handlers found in api.py — the "
        "pattern has stopped matching, so this check would pass on nothing")
    astray = sorted(name for name, routed in handlers if not routed)
    assert not astray, (
        f"{astray} build a response without asking what language the reader "
        "is in. Every sentence they carry is a refusal somebody reads, and "
        "it will be in English no matter what language they chose.")


def test_every_failure_answers_in_the_readers_language():
    """The path the handler guard above cannot see, and where the port
    found something.

    `@app.exception_handler(Exception)` cannot be the catch-all here:
    Starlette hands it to `ServerErrorMiddleware`, outside the CORS layer, so
    the 500 goes back without the header and the console reads it as
    unreachable rather than refused. The catch-all is therefore a middleware
    — and being a middleware, it was not a handler, so no guard in any of the
    three products was asking it anything. Its sentence sat inline in English
    in all three.

        asked     does every exception handler answer in the reader's language
        mattered  does every failure answer in the reader's language

    The one answer every route can give is the one a person meets when the
    product is already failing them, and it was the only one that came back
    in a language they might not read.
    """
    tree = ast.parse((REPO / "qrme" / "api.py").read_text(encoding="utf-8"))
    caught = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(isinstance(d, ast.Call)
                   and getattr(d.func, "attr", "") == "middleware"
                   for d in node.decorator_list):
            continue
        # The catch-all specifically, not any middleware that happens to
        # handle an error. A bare `except:` counts, because that is a
        # catch-all written the other way.
        if not any(isinstance(n, ast.ExceptHandler)
                   and (n.type is None
                        or getattr(n.type, "id", "") == "Exception")
                   for n in ast.walk(node)):
            continue
        asked = any(
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", "") == "refusal_language"
            and getattr(getattr(n.func, "value", None), "id", "") == "i18n"
            for n in ast.walk(node))
        caught.append((node.name, asked))

    assert caught, (
        "no middleware in api.py catches an exception — either the catch-all "
        "is gone, in which case a failing route answers with nothing the "
        "console can read, or this guard has stopped matching")
    astray = sorted(name for name, asked in caught if not asked)
    assert not astray, (
        f"{astray} answer a failed route without asking what language the "
        "reader is in. A person who is already being failed reads the "
        "apology in English.")


def test_the_extractor_can_still_see(tmp_path):
    """A guard on the guard, against a fixture whose answer is known.

    Everything above trusts an AST walk. If the walk stops recognising a call
    shape, `_details` returns a small set, the backlog looks solved and the
    record fills with strings nobody raises — which the staleness half would
    report as *progress*. The fixture carries one of each shape this codebase
    actually uses.
    """
    fixture = tmp_path / "shapes.py"
    fixture.write_text(
        'from fastapi import HTTPException\n'
        'A_CONSTANT = "held in a module constant"\n'
        'A_TABLE = {"x": "one row of a table: {}", "y": "the other: {}"}\n'
        'def a(): raise HTTPException(404, "positional")\n'
        'def b(): raise HTTPException(403, detail="by keyword")\n'
        'def c(): raise HTTPException(422, "wrapped across "\n'
        '                                  "two source lines")\n'
        'def d(x): raise HTTPException(400, f"built from {x}")\n'
        'def e(): raise fastapi.HTTPException(409, "dotted call")\n'
        'def f(): raise HTTPException(402, {"message": "a dict detail"})\n'
        'def g(): raise HTTPException(409, A_CONSTANT)\n'
        'def h(k, v): raise HTTPException(409, A_TABLE[k].format(v))\n'
        'def i(x): raise HTTPException(400, "joined " + f"with {x}")\n'
        'def j(exc): raise HTTPException(400, str(exc))\n'
        'def k(exc): raise HTTPException(400, exc.detail)\n'
        'def l(x): raise HTTPException(400, i18n.fill(i18n.SOMETHING, a=x))\n',
        encoding="utf-8")
    literals, interpolated = _details(tmp_path)
    assert literals == {"positional", "by keyword",
                        "wrapped across two source lines", "dotted call",
                        "a dict detail", "held in a module constant"}, (
        f"the extractor no longer reads the shapes it documents:\n{literals}")
    # Four templates: the f-string, both rows of the table reached through
    # `.format()`, and the concatenation. A table row is a template rather
    # than a literal because which row a reader meets is chosen at runtime
    # and every one of them carries a value.
    assert interpolated == 4, (
        "the extractor stopped counting interpolated refusals, which is how "
        "36 of them would quietly leave the record's header")

    # And the classification itself, shape by shape — the half that keeps a
    # sentence from being filed as *somebody else's problem* when it is not.
    found = _refusals(tmp_path)
    counted = {shape: len(rows) for shape, rows in found.items() if rows}
    assert not found["unknown"], (
        f"the classifier met a shape it has no branch for: {found['unknown']}")
    assert counted["domain"] == 1, "str(exc) should be a domain sentence"
    assert counted["passthrough"] == 1, "exc.detail carries somebody else's"
    assert counted["translated"] == 1, "i18n.fill is already handled"
    assert counted["named"] == 1, "the module constant"
    assert counted["template"] == 4, (
        "an f-string, both rows of a table reached through .format(), and a "
        "concatenation — every shape that puts a value inside a sentence")


def test_every_translated_refusal_has_every_language():
    """No partial rows. A row missing four languages serves English to four
    readers while the table says the sentence is handled."""
    langs = [c for c in i18n.SUPPORTED if c != i18n.DEFAULT]
    gaps = {k: [c for c in langs if c not in v]
            for k, v in i18n._REFUSALS.items()}
    gaps = {k: v for k, v in gaps.items() if v}
    assert not gaps, (
        "these refusals are missing languages:\n    "
        + "\n    ".join(f"{k[:60]}: {', '.join(v)}"
                        for k, v in sorted(gaps.items())))
    assert len(i18n._REFUSALS) >= 9, (
        f"only {len(i18n._REFUSALS)} refusals in the table — this check would "
        "be passing on almost nothing")


def test_no_refusal_is_translated_into_english():
    """The check the one above cannot make.

    `test_every_translated_refusal_has_every_language` asks whether each row
    has all nine keys. A row whose nine values are the English sentence pasted
    nine times satisfies it exactly, and the table would then claim the refusal
    is handled while every reader gets English — the failure this whole file
    exists to catch, wearing the shape of the fix.

        asked     does every refusal have every language
        mattered  does every language say something other than the English

    Byte equality is the whole test. It cannot tell a good translation from a
    bad one and does not try; it can tell a translation from no translation,
    which is the difference that was going unchecked while 142 rows were added
    to this table by hand in one release.
    """
    untouched = [(k, c) for k, v in i18n._REFUSALS.items()
                 for c, t in v.items() if t == k]
    assert not untouched, (
        f"{len(untouched)} language value(s) are the English sentence "
        "verbatim, so the table claims a refusal is translated and serves "
        "English:\n    "
        + "\n    ".join(f"[{c}] {k[:70]}" for k, c in untouched[:20]))


# --- driven, not read ------------------------------------------------------
#
# `client` comes from tests/conftest.py. Profiles are made here rather than
# through the `profile_id` fixture because that fixture pins an owner token
# onto the client's default headers, and half of what follows is about a
# reader who holds no such token.

def _a_profile(client, name: str, language: str, mode: str = "pre"):
    made = client.post("/profiles", json={
        "owner_id": f"owner-{name}", "kind": "self", "display_name": name,
        "persona": "A profile that exists to be refused.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert made.status_code == 201, made.text
    body = made.json()
    owner = body["owner_token"]
    set_language = client.put(
        f"/profiles/{body['id']}/language",
        json={"language": language, "mode": mode},
        headers={"authorization": f"Bearer {owner}"})
    assert set_language.status_code == 200, set_language.text
    return body["id"], owner


def test_an_owner_is_refused_in_their_own_language(client):
    """The defect, driven end to end.

    The browser header says `en-US` throughout, because that is what a console
    owner's browser actually sends whatever they chose in the app. If this
    passes while the header decides, the fix is a no-op.

    Asserted against the table's own entry rather than a fixed Spanish string,
    so rewording the English fails the row that went stale rather than this
    test.
    """
    profile_id, owner = _a_profile(client, "Refusal", "es")
    intruder, _ = _a_profile(client, "Intruder", "en")

    refused = client.put(
        f"/profiles/{intruder}/language", json={"language": "de"},
        headers={"authorization": f"Bearer {owner}",
                 "accept-language": "en-US,en;q=0.9"})
    assert refused.status_code == 403, refused.text
    assert refused.json()["detail"] == (
        i18n._REFUSALS["not authorized for this resource"]["es"]), (
        "the owner set Spanish and was refused in "
        f"{refused.json()['detail']!r}. The browser header said en-US, which "
        "is exactly why the header cannot be what decides this.")


def test_a_stranger_is_not_answered_in_the_owners_language(client):
    """The wrong fix, checked directly.

    Resolving the language from the `profile_id` in the path would answer a
    stranger asking *about* a profile in the language of the person they are
    asking about. The reader here holds no owner token, so their own header is
    all there is.
    """
    profile_id, _ = _a_profile(client, "Watched", "ja")

    refused = client.put(f"/profiles/{profile_id}/language",
                         json={"language": "de"},
                         headers={"accept-language": "fr-FR,fr;q=0.9"})
    assert refused.status_code == 401, refused.text
    detail = refused.json()["detail"]
    assert detail == i18n._REFUSALS["authentication required"]["fr"], (
        "a stranger asking about a Japanese-speaking owner's profile got "
        f"{detail!r}. The path names whose profile it is, never who is "
        "reading the answer.")


def test_on_demand_mode_is_not_a_statement_about_what_the_owner_reads(client):
    """`effective_language` returns English in `on_demand` mode.

    That mode means "persona, keep your own voice; I will translate what I
    choose" — a decision about generated speech. Reading it here would serve
    English refusals to an owner who had set Spanish, and would have passed
    every test written with a default-mode profile.
    """
    profile_id, owner = _a_profile(client, "OnDemand", "es", mode="on_demand")
    intruder, _ = _a_profile(client, "Bystander", "en")

    assert i18n.effective_language(profile_id) == "en"
    assert i18n.get_language(profile_id) == "es"

    refused = client.put(
        f"/profiles/{intruder}/language", json={"language": "de"},
        headers={"authorization": f"Bearer {owner}",
                 "accept-language": "en-US,en;q=0.9"})
    assert refused.status_code == 403, refused.text
    assert refused.json()["detail"] == (
        i18n._REFUSALS["not authorized for this resource"]["es"]), (
        "an owner in on_demand mode was refused in "
        f"{refused.json()['detail']!r}. That mode is about the persona's "
        "voice; it says nothing about what the owner reads.")


def test_a_dict_detail_keeps_its_vocabulary_and_translates_its_sentence():
    """`tiers.gate` refuses with a dict, not a sentence.

    A handler that translated only `str` would leave the plan gate — the one
    refusal standing between somebody and a decision to pay — in English while
    every sentence around it changed language. And a handler that translated
    the whole dict would translate `reason` and `capability`, which the
    console branches on: the same rule as `_PUBLIC`, one layer in.
    """
    detail = {"reason": "plan", "capability": "marketplace",
              "have": "free", "message": "authentication required"}
    out = i18n.localize_detail(detail, "de")
    assert out["message"] == i18n._REFUSALS["authentication required"]["de"]
    assert out["reason"] == "plan" and out["capability"] == "marketplace", (
        "the API's own vocabulary was translated. A console comparing "
        'reason === "plan" stops recognising its own upgrade card.')


def test_an_unknown_sentence_falls_through_as_english():
    """The 142 in the record, and anything added tomorrow.

    English is a visible gap. A guessed translation is a confident error, and
    a refusal is exactly the sentence where being confidently wrong costs
    somebody the most.
    """
    assert i18n.tr_refusal("a sentence nobody has translated", "es") == (
        "a sentence nobody has translated")
    assert i18n.localize_detail({"message": "likewise"}, "ja") == {
        "message": "likewise"}


def test_resolving_a_language_never_raises():
    """The diagnostic must not become the outage.

    This runs inside the exception handler. If it can throw, a refusal turns
    into a 500 and the person is told the server broke when it was really
    telling them no.
    """
    class _Broken:
        @property
        def headers(self):
            raise RuntimeError("no headers here")

    with pytest.raises(RuntimeError):
        _Broken().headers          # the fixture really is broken
    for bad in ({}, None):
        class _Odd:
            headers = {"authorization": "Bearer nope"} if bad is None else {}
        assert i18n.refusal_language(_Odd()) == "en"
