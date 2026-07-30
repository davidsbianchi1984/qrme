# QRME v0.18.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.18.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.18.0** — the shells catch up, and so do the drawings.

The two features that had gained console doors but no native ones now
have them. **Who wrote this?** reaches Manage on iOS, Android and
Windows — paste a passage and it names the profile that produced it, from
the text alone, showing matched passages out of stored rather than a bare
yes, and naming nobody at all below the 0.25 threshold. **The role
picker** reaches the chat composer on all three, defaulting to "read my
prompt" and reporting back which role applied *and whether it was
declared or inferred*, so an inference is never handed back as an
instruction.

That completes something two earlier rounds each claimed and neither
finished: every feature with a door in the web console now has one in the
native shells.

**And the drawings caught up.** Voice cloning, the recoverable watermark
and the role all shipped with no screen, no lesson, and no way for the
in-app helper to point at them — for two whole versions. Three screens
join the gallery (**147 Your Own Voice**, **148 Who Wrote This?**, **149
How Should They Work?**), each with a lesson in its proper chapter, each
reachable by asking the helper in the words somebody would actually type:
"clone my voice", "who wrote this", "just do it".

**Fixed** — `SmallAction` on Android took no `enabled` parameter, so a
busy or empty action looked live and merely ignored taps. It takes one
now, and the label dims with it.
