# QRME v0.11.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.11.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.11.0** — the console catches up with its backend. One of three
interoperating products, all three cut together at this version.

### The doors were always there; now you can see them

Friends, the marketplace, the starter collection, rooms and live desks
have existed as API surfaces for many releases. The desktop console
finally shows them:

- **Discover** — browse the marketplace by tag, and install the
  **33-profile starter collection** with one press: tradespeople,
  teachers, artists, each carrying its industry's knowledge pack, each a
  real profile you can befriend and talk to.
- **Friends** — the list, with the **founder pinned first**: David
  Bianchi and his synthetic profile stand at positions one and two on
  every list, by design, and now visibly.
- **Rooms** — open and join rooms across every channel: 2D text, 2D
  audio, 2D video, **AR** and **VR** — plus the live desks with their
  presence lights. AR and VR rooms carry an honest badge: step inside
  from a headset or phone; the desktop shows the room.

### The memory vault names names

One row per remembered conversation — *Dana with June Bianchi · 12 turns
· last Tuesday* — never "profile" and "interactor". View any
conversation, and **erase exactly the one you choose**.

### Chat's fallback stopped performing a character

"[stub reply in a warm tone to: hi]" was a stage direction leaking into
the play. The fallback now speaks plainly: it quotes what it heard, says
no model answered, and names both doors out — a provider key, or Ollama
for a free local model.

### Verification

1194 tests green, including that the vault lists conversations by real
names and erases one at a time, that rooms list with their channels, that
desks list with their presence, and that the fallback carries no stage
directions.

### Install

If you have 0.7.0 or later, this arrives on its own — one restart when
prompted.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
