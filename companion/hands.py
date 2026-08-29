"""The motor: the half of the hands that actually moves.

QRME holds the authority, the deciding and the ledger. It cannot move a
cursor, and it should not be able to — the stack runs on a server in a
data centre and the screen being worked is on somebody's desk. This
program is the piece that closes that gap, and it runs **on the person's
own machine**, started by them, stopped by them.

    see      one picture of this screen
    decide   the stack chooses ONE move, inside the grant
    act      this program performs it
    record   the stack already wrote it down before it was performed

## What it is not

It is not a service, it does not install, and it does not start with the
machine. It runs in a terminal where somebody can watch it and holds
nothing when it exits: no credential on disk, no daemon, no autostart.
A motor that survives the person who started it is the thing people are
right to be afraid of.

It also holds **no authority of its own**. Every move it makes was chosen
and permitted on the other side; this end asks "what next" and is told,
or is told nothing. If the grant expires mid-errand the next answer is a
refusal and the loop stops — there is no local copy of the permission to
go stale.

## Running it

    pip install pyautogui mss
    python companion/hands.py --base https://your-deployment \\
        --profile prf_... --token OWNER_TOKEN --reach rch_...

`--dry-run` is the default: it prints each move instead of performing it,
so the first thing anybody sees is what it *would* do. Pass `--live` to
let it touch the machine.

**The stop is the mouse.** PyAutoGUI's failsafe is on: throw the pointer
into a screen corner and the next move raises rather than lands. That is
deliberately a physical gesture rather than a key combination, because a
key combination is something a hand that has the keyboard could type.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import sys
import time
import urllib.error
import urllib.request

#: How long to wait between rounds when nothing said otherwise. Slow on
#: purpose: a person has to be able to watch this happen and stop it, and
#: a loop that outruns the eye is a loop nobody can supervise.
BEAT = 1.5

#: The most rounds one run will take before it stops and says so. The
#: grant carries its own step budget on the other side; this is the
#: local belt — a companion that cannot loop forever cannot be left
#: looping forever by accident.
ROUNDS = 200


def _post(base: str, path: str, token: str, body: dict) -> dict:
    request = urllib.request.Request(
        base.rstrip("/") + path, method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=120) as answer:
            return json.loads(answer.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            said = json.loads(exc.read().decode("utf-8")).get("detail")
        except Exception:
            said = None
        raise SystemExit(f"the stack refused: {said or exc.code}") from None


def _frame() -> str:
    """One picture of the primary screen, as base64 PNG."""
    import mss
    from PIL import Image

    # `mss.mss` is the old spelling and warns on newer releases; `MSS` is
    # the same object under the name it will keep.
    screens = getattr(mss, "MSS", None) or mss.mss
    with screens() as grab:
        shot = grab.grab(grab.monitors[1])
    picture = Image.frombytes("RGB", shot.size, shot.rgb)
    # Sent small. The eyes read a layout, not a font: a full 4K frame
    # costs real money per round and reads no better.
    picture.thumbnail((1280, 1280))
    held = io.BytesIO()
    picture.save(held, format="PNG")
    return base64.b64encode(held.getvalue()).decode("ascii")


def _perform(step: dict, live: bool) -> str | None:
    """Do one move on this machine. Returns why it could not, or None."""
    verb = step["verb"]
    detail = step.get("detail") or {}
    target = step.get("target") or ""
    if not live:
        print(f"    would {verb} {target} {detail or ''}".rstrip())
        return None

    import pyautogui
    # The corner failsafe, on. See the module docstring: the stop is a
    # gesture the hand on the keyboard cannot make for you.
    pyautogui.FAILSAFE = True

    if verb == "move":
        wide, tall = pyautogui.size()
        pyautogui.moveTo(float(detail.get("x", 0.5)) * wide,
                         float(detail.get("y", 0.5)) * tall, duration=0.2)
    elif verb == "press":
        pyautogui.click()
    elif verb == "type":
        # Typed rather than pasted: a clipboard is shared with everything
        # else running, and borrowing it to move text is a side effect on
        # somebody's machine that nobody asked for.
        pyautogui.typewrite(str(detail.get("text", "")), interval=0.02)
    elif verb == "key":
        name = str(detail.get("key", ""))
        pyautogui.hotkey(*name.split("+")) if "+" in name \
            else pyautogui.press(name)
    elif verb == "scroll":
        pyautogui.scroll(int(-float(detail.get("dy", 0)) / 4) or -1)
    elif verb == "wait":
        time.sleep(min(float(detail.get("seconds", 1)), 20))
    else:
        return f"this end has no way to {verb}"
    return None


def main() -> None:
    ask = argparse.ArgumentParser(description=__doc__)
    ask.add_argument("--base", required=True, help="the deployment's URL")
    ask.add_argument("--profile", required=True)
    ask.add_argument("--token", required=True, help="the profile's owner token")
    ask.add_argument("--reach", required=True, help="an open reach")
    ask.add_argument("--live", action="store_true",
                     help="actually touch this machine (default: print only)")
    ask.add_argument("--beat", type=float, default=BEAT)
    said = ask.parse_args()

    # The command line is copied off a screen, and a half-copied one used
    # to end in a urllib traceback about an "unknown url type" — which
    # says nothing about the thing that is actually wrong.
    if not said.base.startswith(("http://", "https://")):
        raise SystemExit(
            f"--base must be the deployment's URL, starting http:// or "
            f"https:// — got {said.base!r}. Copy the whole command from "
            f"the Hands screen; it comes with your own values in it.")

    where = (f"/profiles/{said.profile}/hands/reaches/{said.reach}")
    print(f"watching {said.base} · {said.reach} · "
          f"{'LIVE' if said.live else 'dry run'}")
    if said.live:
        print("  the stop is your mouse: throw the pointer into a corner.")

    for round_number in range(ROUNDS):
        step = _post(said.base, where + "/next", said.token,
                     {"frame": _frame()})
        verb = step.get("verb")
        outcome = step.get("outcome")
        note = step.get("note") or ""
        print(f"  {step.get('n')}. {verb} {step.get('target') or ''} "
              f"[{outcome}] {note}".rstrip())

        if outcome != "done":
            # Refused, and already written down on the other side. There
            # is nothing here to perform and nothing to argue with.
            continue
        if verb == "done":
            print("finished.")
            return
        if verb == "ask":
            print("it needs you. nothing further will happen on its own.")
            return

        why = _perform(step, said.live)
        if why:
            print(f"    {why}")
        time.sleep(max(0.2, said.beat))

    print(f"stopped after {ROUNDS} rounds without finishing.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped.", file=sys.stderr)
