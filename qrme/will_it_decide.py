"""Ask a provider the question the hands ask, and print what comes back.

    asked     which model will actually choose a move on a screen
    mattered  finding out cost a grant, a reach, a command line and a
              rebuild, per candidate

Deciding a move on somebody's screen is the one call this platform makes
that a provider may decline as a class — one answers with a plain
refusal and no content at all. Which of them will take the work is each
vendor's policy and it changes, so it is a thing to measure rather than
predict.

This asks exactly `hands._decision_prompt` builds, with a written screen
standing in for a photographed one, so the answer here is the answer the
hands would get. Nothing is granted, no reach is opened, no ledger is
written and no cursor exists.

    docker compose -f docker/beta-compose.yml --env-file .env \
        exec qrme python -m qrme.will_it_decide vault ollama anthropic

With no names it tries every provider that is configured.
"""

from __future__ import annotations

import sys

from . import hands, llm

#: A screen in words, of the kind `read_screen` returns: an ordinary
#: text editor with somewhere to type. Nothing here is a trick or an
#: edge case — if a provider will not choose a move on this, it will not
#: choose one on anything.
SCREEN = ("A Notepad window fills the screen, titled Untitled - Notepad. "
          "Under the File / Edit / View menus there is one large empty "
          "white text area with the cursor blinking at the top left. "
          "The status bar reads Ln 1, Col 1.")

ERRAND = "type the word yellow in notepad"


def _one(name: str) -> tuple[str, str]:
    """(verdict, detail) for one provider, never raising."""
    reach = {"errand": ERRAND, "platform": "windows", "mode": "acting"}
    system, question = hands._decision_prompt(
        reach, ["look", "press", "type", "key", "ask", "done"], SCREEN, [])
    try:
        said = llm.get_provider(choice=name).generate(
            system, [{"role": "user", "content": question}])
    except Exception as exc:  # a provider that cannot be built is an answer
        return "ERROR", f"{type(exc).__name__}: {exc}"[:160]
    if not said or not said.strip():
        return "SILENT", "no answer at all — see the log for a stop reason"
    first = said.strip().splitlines()[0]
    match = hands._CHOICE.match(first)
    verb = (match.group(1) if match else "").strip().lower()
    if verb not in hands.VERBS:
        return "UNPARSED", first[:160]
    if verb in ("ask", "look"):
        return "HEDGED", first[:160]
    return "DECIDED", first[:160]


def main(names: list[str]) -> None:
    if not names:
        names = [p["name"] for p in llm.available() if p["configured"]]
    width = max(len(n) for n in names)
    print(f"errand: {ERRAND}\n")
    for name in names:
        verdict, detail = _one(name)
        print(f"  {name:<{width}}  {verdict:<8}  {detail}")
    print("\nDECIDED is one that will work the screen. HEDGED answered but "
          "would not move.\nSILENT and ERROR will not do the job at all.")


if __name__ == "__main__":
    main(sys.argv[1:])
