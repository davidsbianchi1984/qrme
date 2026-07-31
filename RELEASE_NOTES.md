# QRME v0.22.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.22.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.22.0 — the audit reaches zero, and finds five more defects on the way.**

Five rounds. Each built a console door for a backend feature that had none,
and in **every one of them** building the door found a defect in the thing it
was a door to. In every one of those, the argument against the defect was
already written down somewhere else in the same repository — usually a few
lines away, occasionally in the docstring directly above.

| | at the start of this release | now |
|---|---|---|
| Console-doorless routes | 64 | **0** |
| `api.ts` bindings nothing calls | 25 | **0** |

Both record files are now **empty rather than short**, and the tests that read
them assert emptiness.

## The only post that actually leaves was the one going out unmarked

`POST /social/{cid}/publish` writes a profile's words to a platform QRME does
not run. It is the single route in this product where synthetic media
genuinely **leaves the building** — and it stored that post with
`watermark_id` NULL, while `compose_post`, the in-app equivalent, stamped a
credential every time.

`compose_post` even says why, in a sentence that describes the *other* route
more exactly than the one it is written above: *a public post is synthetic
media leaving the platform: it carries a verifiable synthetic-media credential
from the moment it exists.* So the only posts going out unmarked were the ones
actually going out.

The same function ran the profile's own `maturity` as its moderation filter,
where `compose_post` forces `strict` with the note *public posts face the
widest audience: always the strict filter*. A profile set to `open` was held to
the loosest rule on the way to an audience QRME cannot see, and the strictest
one when posting where it can.

## Anybody could take away the name a profile answers to

`PUT /profiles/{id}/handle` took **no credential of any kind**. The damage is
not that a stranger could give a profile a second name — claiming a handle
deletes the existing one first, because that is how *changing* your handle
works. So anybody could take `@rosa` away from Rosa: every printed reference,
shared link and beacon naming her went dead at once, and the name she now
answered to was picked by whoever did it.

The three beacon routes **immediately below this one in the same file** were
given exactly this check in an earlier pass, and `place_beacon` states the
reason in words that fit here without changing a syllable.

## A post the filter refused was published by the route that lists what was published

`compose_post` stores a held post `pending` and returns `content: None` **to
the owner who just asked for it**. Fourteen lines further down, `list_posts`
returned every column of every row, whatever its status, to anybody, with no
token. The hold was enforced against the author and against nobody else — and
`flag_reason` went with it, naming the rule the text broke.

## An id was read as a credential, in the feature built on consent

`/connections` had no authentication at all. Speak as anybody, read anybody's
conversation, and end one with no id and no token.

## A guest joining a stream minted the room before the 401

The anonymous path created the desk's room and *then* refused the caller.

## Two guards that could only pass while the problem existed

`test_the_union_is_still_wider_than_the_console` asserted the union backlog was
*strictly* smaller than the console's, reasoning that if the two ever agreed
the likelier cause was a broken native extractor than a console that had caught
up. Sound while catching up was hypothetical. It now asserts the invariant that
survives — the union can never exceed the console's, since the console is one of
its own surfaces — and the liveness check it was doubling for moved to
`test_each_native_shell_is_still_being_read`, which counts call sites per shell
and would actually notice.

## Also in this release

**Six new console screens** (178–183): signing a document, the visitor's side
of a desk, meeting a stranger, the mark on a post, what a profile says and in
which language, and the remainder — the last eighteen routes, wired as one
lookup control rather than nine buttons nobody would find.

The iOS, Android and Windows shells carry the same credentials the console
now does, on connections and on claiming a handle.

**Suite: 2027 passing.**

---

Cut in step with [JIM-mini](https://github.com/davidsbianchi1984/jim-mini) and
[PDI](https://github.com/davidsbianchi1984/pdi), both also at v0.22.0, both of
which reached zero on the same audit in this release.
