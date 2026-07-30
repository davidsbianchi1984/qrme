# QRME v0.17.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.17.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.17.0** — the voice reaches the microphone, and the Wall gets its hands back.

Voice enrollment reaches the three devices that actually have a microphone
in them. iOS, Android and Windows each gain a **Voice** screen walking
FIG. 800's order — permission, collection, the characteristics, the print
— but *recording* the sample and measuring it, where the web console could
only ask the owner to type how many seconds they had gathered. The privacy
property holds structurally rather than by promise: the recording stays in
the app's own container and only the measurement crosses the wire, with
`reference` naming the file, so no voice corpus can accumulate
server-side. Turn counting states its method per platform rather than
inventing a number it cannot stand behind.

Three features came out from behind the API, because a door nobody can
open reads in the field as the feature not existing: a **Voice** tab, a
**role picker** in the composer (advisor, collaborator, operator, or
"let it read my prompt"), and **"Who wrote this?"** in Control — paste any
text and it names the profile that produced it, from the text alone.

The watermark learned to survive being edited. `POST /watermarks/recover`
answers *whose work is this?* without a credential id and keeps answering
after the text has been rewritten, using keyed five-word windows compared
by overlap. Below a 0.25 threshold it names nobody, because a coincidence
must not read as an accusation.

**Fixed, and this one was live:** every like, comment and share on the
community wall returned 404. The audience routes map a plural path segment
to a kind (`posts` → `post`), and the console was asking for the
singular — so the buttons had never worked, in any release that had them.
The backend tests passed because they used the plural; the console
compiled because a template literal is only a string. Both halves are now
checked against each other. Also fixed: the Windows navigation pane
rendered the literal strings `tab.desk` and `tab.signatures`.
