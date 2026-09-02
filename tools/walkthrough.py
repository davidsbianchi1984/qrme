"""Drive every road on the map, and photograph it driven.

The 3.0.0 gate's own words: someone picks any road on the map and
drives it to the end without finding a wall. This harness is that
drive, automated — the same booted backend and built console the
camera uses, walked road by road over real HTTP, with a screenshot
of each road in a *driven* state saved to ``docs/walkthrough/``.

A road passes when every door on it answers the way the product says
it will — including an honest refusal where this machine lacks a key
(a spoken limit is not a wall; a dead end that says nothing is). The
report never invents: every verdict line carries the status codes
that actually came back.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))

import shoot_screens as camera

OUT = REPO / "docs" / "walkthrough"
BIRTHDATE = "1984-05-01"


def call(method: str, path: str, body=None, token: str | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(camera.BASE + path, data=data,
                                 method=method)
    req.add_header("content-type", "application/json")
    if token:
        req.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


def owner_token_for(profile_id: str) -> str:
    """The product's own issuer, on the walkthrough's own database."""
    from qrme import auth
    return auth.issue("owner", profile_id)


class Drive:
    def __init__(self):
        self.rows: list[tuple[str, str, bool]] = []

    def step(self, road: str, note: str, ok: bool):
        self.rows.append((road, note, ok))
        print(("  ok  " if ok else "  WALL") + f"  {road}: {note}")

    def walls(self):
        return [r for r in self.rows if not r[2]]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    camera.build_console()
    proc = camera.start_backend()
    session = camera.seed("/tmp/shots.db")
    d = Drive()
    me = session["profileId"]
    own = session["ownerToken"]
    try:
        # A second profile to talk to, and an interactor to be.
        s, p = call("POST", "/profiles", {
            "owner_id": session["accountId"], "kind": "fictional",
            "display_name": "June Okafor",
            "persona": "A baker who opens at seven and says so.",
            "verification": {"birthdate": BIRTHDATE}})
        d.step("setup", f"a profile to meet ({s})", s == 201)
        pal, pal_token = p.get("id"), p.get("owner_token")
        s, i = call("POST", "/interactors", {"birthdate": BIRTHDATE})
        d.step("setup", f"an interactor to be ({s})", s == 201)
        actor, actor_token = i.get("id"), i.get("token")
        s, _ = call("PUT", f"/profiles/{pal}/relationships/{actor}",
                    {"relationship_type": "friend", "nickname": "me",
                     "tone": "warm"}, pal_token)
        d.step("setup", f"the relationship set ({s})", s == 200)

        # 1 · Chat
        s, r = call("POST", f"/profiles/{pal}/chat",
                    {"interactor_id": actor,
                     "message": "When do you open tomorrow?"},
                    actor_token)
        said = bool(((r or {}).get("profile_message") or {})
                    .get("content"))
        d.step("chat", f"a typed line gets a reply ({s})", s == 200 and said)

        # 2 · Voice — the voices door answers, and the reply above is
        # what the talk face speaks; no key, honest state either way.
        s, v = call("GET", "/voices")
        d.step("voice", f"the voices door answers ({s})", s == 200)

        # 3 · Avatar — the deck and the forge say their honest state.
        s, a = call("GET", "/avatars/market")
        d.step("avatar", f"the avatar market answers ({s})", s == 200)
        s, a = call("GET", "/avatars/forge")
        d.step("avatar", f"the forge says its state ({s})", s == 200)

        # 4 · Video — doors honest, the direction takes an edit, and the
        # render road is set through its owner-gated door.
        s, doors = call("GET", "/video/doors")
        honest = s == 200 and ("configured" in doors)
        d.step("video", f"the film doors answer ({s}, configured="
               + str(doors.get("configured")) + ")", honest)
        s, _ = call("POST", f"/video/direction/{pal}",
                    {"asked": "warmer light, behind the counter",
                     "surface": "walkthrough"})
        d.step("video", f"the direction takes an edit ({s})", s == 200)
        # The road door spends money, so it takes the owner's token — a
        # stranger is turned away, the owner gets through. Both halves
        # driven: the refusal is the proof the gate is real.
        s, _ = call("POST", f"/video/road/{pal}",
                    {"road": "video", "daily_seconds": 60})
        d.step("video", f"the road door refuses a tokenless caller ({s})",
               s in (401, 403))
        s, road = call("POST", f"/video/road/{pal}",
                       {"road": "video", "daily_seconds": 60},
                       token=pal_token)
        d.step("video", f"the owner sets the video road ({s})",
               s == 200 and road.get("road") == "video")

        # 5+6 · The stage's platform shelf, and a room to stand it on.
        s, x = call("GET", "/rooms/xr-platforms")
        d.step("ar/vr", f"the XR shelf answers ({s})", s == 200)
        s, room = call("POST", "/rooms",
                       {"topic": "The walkthrough",
                        "participants": [
                            {"kind": "user", "id": actor},
                            {"kind": "profile", "id": pal}]},
                       actor_token)
        rid = (room or {}).get("id") or (room or {}).get("room", {}).get("id")
        d.step("rooms", f"a room opens ({s})", s in (200, 201) and bool(rid))
        if rid:
            s, _ = call("POST", f"/rooms/{rid}/messages",
                        {"sender_id": actor,
                         "message": "Anyone here?"}, actor_token)
            d.step("rooms", f"a said line lands ({s})", s in (200, 201))
            # The turn was taken on a profile now on the video road, so the
            # footage door is asked what it holds. On a deployment with a
            # render service the row is pending; on this one there is none,
            # and that is the honest answer, not a wall — the road was set,
            # the turn was taken, and the door reports the truth of both.
            s, latest = call("GET", f"/video/latest/{pal}")
            d.step("video", f"the footage door answers honestly ({s})",
                   s == 200 and "scene" in (latest or {}))

        # 7 · The watch
        s, w = call("GET", f"/profiles/{me}/watch", token=own)
        d.step("watch", f"the wrist payload answers ({s})", s == 200)

        # 8 · A profile through its connections — the catalogue, and
        # the honest state of each direction.
        s, c = call("GET", "/connectors/catalog")
        d.step("connections", f"the connector catalogue answers ({s})",
               s == 200)

        # 9 · The Company Builder, end to end.
        s, co = call("POST", "/companies",
                     {"name": "Walk & Daughters", "industry": "bakery",
                      "headcount": 3}, own)
        d.step("companies", f"founded ({s})", s == 201)
        cid = (co or {}).get("id")
        seat = hired = None
        if cid:
            s, seat = call("POST", f"/companies/{cid}/seats",
                           {"title": "Counter clerk",
                            "department": "Front of house"}, own)
            d.step("companies", f"a seat opens ({s})", s == 201)
        if seat and seat.get("id"):
            s, _ = call("POST",
                        f"/companies/{cid}/seats/{seat['id']}/interview",
                        token=own)
            d.step("companies", f"the interview composes ({s})", s == 201)
            s, hired = call("POST",
                            f"/companies/{cid}/seats/{seat['id']}/hire",
                            {"answers": [
                                {"question": "Full name:",
                                 "answer": "June Walker"},
                                {"question": "Duties:",
                                 "answer": "Counter, case, till."},
                                {"question": "Decides vs escalates:",
                                 "answer": "Substitutions; refunds up."}]},
                            own)
            d.step("companies", f"the hire signs ({s})", s == 201)
            s, _ = call("POST", f"/companies/{cid}/publish",
                        {"tagline": "Warm at seven."}, own)
            d.step("companies", f"open for business ({s})", s == 201)
        if hired and hired.get("profile_id"):
            s, t = call("POST",
                        f"/profiles/{hired['profile_id']}/export/ticket",
                        token=owner_token_for(hired["profile_id"]))
            d.step("companies", f"the hand-out ticket mints ({s})",
                   s == 201 and t.get("single_use") is True)

        # 10 · Wearables: pair, point at a guardian, verify.
        s, _ = call("POST", f"/profiles/{me}/wearables",
                    {"name": "Oura", "kind": "ring"}, own)
        d.step("wearables", f"a ring pairs ({s})", s == 201)
        s, _ = call("PUT", f"/profiles/{me}/wearables/Oura/guardian",
                    {"drip_url": "https://jim.example/watch/drip/walk"},
                    own)
        d.step("wearables", f"the guardian road is set ({s})", s == 200)
        s, w = call("POST", f"/profiles/{me}/wearables/Oura/verified",
                    {"device_name": "Oura Ring Gen3", "battery": 71}, own)
        d.step("wearables", f"the pairing is vouched for ({s})",
               s == 200 and bool(w.get("verified_at")))

        # 11 · The marketplace
        s, shops = call("GET", "/shops")
        d.step("market", f"the shops answer ({s})", s == 200)

        # The photographs: each road's screen, in its driven state.
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/opt/pw-browsers/chromium")
            page = browser.new_page(viewport=camera.VIEWPORT,
                                    device_scale_factor=2)
            page.goto(camera.BASE + "/", wait_until="networkidle")
            page.evaluate("s => localStorage.setItem('qrme.session', s)",
                          json.dumps(session))
            page.reload(wait_until="networkidle")
            for tab, name in (("chat", "01-chat"),
                              ("rooms", "02-rooms"),
                              ("companies", "03-companies"),
                              ("assist", "04-assist"),
                              ("market", "05-market"),
                              ("shop", "06-shop")):
                try:
                    if camera.open_tab(page, tab):
                        camera.answer_the_notice(page)
                        time.sleep(1.2)
                        page.screenshot(path=str(OUT / f"{name}.png"))
                        d.step("photo", f"{name} photographed", True)
                    else:
                        d.step("photo", f"{tab} tab did not open", False)
                except Exception as e:
                    d.step("photo", f"{tab}: {e}", False)
            browser.close()
    finally:
        proc.terminate()

    walls = d.walls()
    print()
    print(f"{len(d.rows)} steps, {len(walls)} wall(s)")
    for road, note, _ in walls:
        print(f"  WALL  {road}: {note}")
    return 1 if walls else 0


if __name__ == "__main__":
    raise SystemExit(main())
