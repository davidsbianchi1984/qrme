"""One home for the numbers that say *the reader is still reading*.

## Where this came from

Two rounds running found the same defect in two different instruments, and
0.58.9 closed by naming the general case rather than the instance: a floor
written when the surface was small, never raised as the surface grew. The
route reader's floor was set when the console was the only client. The
localizer's was ten, against nine hundred and forty-five.

Both were fixed one file at a time. This is the sweep, and the sweep needed a
convention before it needed code, because a floor is spelled a dozen ways —
`assert len(found) > 20`, `assert total >= 40`, a `FLOORS` tuple, a bare
`_MIN_PATHS`. Nothing could walk them all and ask the only question that
matters about a floor:

    asked     is the number satisfied
    mattered  is the number still near what it measures

## What a Ratchet is

A floor plus **the way to measure the same quantity now**. That second half is
the whole convention: a number with no attached measurement cannot be audited,
which is why 91 of them in this product had drifted to a fiftieth of the truth
without anything noticing.

Registering one has three effects. The number lives in one place instead of
inside an assertion. `test_a_floor_is_within_sight_of_what_it_measures.py`
checks it against reality every run. And it leaves the unregistered-floor
backlog, which only shrinks.

## What the sweep found on its first run

Every reachable floor in the estate was decoration by the standard 0.58.8 set
for itself — a floor below half of what it measures is not holding anything:

    l10n asked, per shell        10 against 945-961     ratio 0.01
    l10n held, per shell         20 against 1087-1115   ratio 0.02
    path literals, all surfaces  40 against 1407        ratio 0.03
    console call sites          200 against 429         ratio 0.47

The last is the one worth reading twice. 0.58.8 wrote that *the console is
protected* and built that round on it. It is protected against being blinded
outright. It was never protected against being halved, and half of a route
reader is half an audit.

`test_the_console_is_a_client_too.py` carried the reason in its own docstring:
the floor of twenty was set low deliberately *because the three products'
shells differ by a factor of three in size*. One number written to work in
three repositories at once is a number set by the smallest of them — 20 held
against PDI's thirty-four bindings and against QRME's four hundred and thirty
equally, which is to say it held nothing here.

That is why these live per product, measured per product, and not in a shared
constant.

## The floors are ratchets, not targets

Each records what its reader reaches today, set at roughly four-fifths. Raising
one when the surface grows is ordinary. Lowering one is a deliberate edit that
shows up in a diff, and the only honest reason is a surface that genuinely got
smaller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Ratchet:
    """A floor, and how to read the same quantity now.

    `measure` is deliberately a callable rather than a recorded number. A
    recorded number would go stale in exactly the way this file exists to
    catch — it would be a second floor needing its own audit.
    """

    name: str
    floor: int
    measure: Callable[[], int]
    why: str


def _l10n(shell: str, half: str) -> Callable[[], int]:
    def go() -> int:
        from . import test_a_shell_asks_for_a_key_it_has as m
        return len((m._asked if half == "asked" else m._held)(shell))
    return go


def _calls(lang: str) -> Callable[[], int]:
    def go() -> int:
        from . import clientpaths
        return len(clientpaths.calls(getattr(clientpaths, lang.upper())))
    return go


def _route_table() -> int:
    from qrme.api import app

    from . import clientpaths
    return len(clientpaths.all_routes(app))


def _path_literals() -> int:
    from . import clientpaths
    from .test_the_extractor_knows_every_call_shape import SURFACES
    return sum(len(clientpaths.paths(lang)) for lang in SURFACES.values())


def _console_files() -> int:
    from .test_a_value_in_a_script_is_not_markup import console_files
    return len(console_files())


def _markup_strings() -> int:
    from .test_a_page_never_prints_what_it_was_given import scanned
    return scanned()


# -- measures that have to run to be counted ---------------------------------
#
# Five floors in `unregistered_floors.txt` stood under *what a live drive
# reached*, and every other measure in this file is a static scan. A scan of
# the population is the wrong denominator for them: most of a client's
# templates carry an id the fixture cannot substitute and are unreachable by
# construction, so measuring 25 against the Swift client's bindings would
# demand a floor above anything the drive can ever reach.
#
#     asked     how much of this client exists
#     mattered  how much of it did the probe actually reach
#
# The two erase measures came here for a different reason. Both read
# `db.connect()`, which answers about whichever database the process is
# pointed at — inside the suite one fixture's temporary file, chosen by
# whatever ran last; alone, the repository's own. The number moved with the
# run, so the audit compared the floor against a different quantity each time
# and could report on neither. They get a database of their own.
#
#     asked     is the floor near what it measures
#     mattered  is it measuring the same thing twice


def _in_a_fresh_qrme(work):
    """Run `work()` against an empty QRME, then put the room back.

    The environment is borrowed and restored: this runs inside a suite whose
    own fixtures point `QRME_DB` at their own temporary files, and a measure
    that left the pointer moved would be a guard breaking the run it audits.
    """
    import os
    import pathlib
    import tempfile
    from qrme import db as qrme_db

    kept = {name: os.environ.get(name) for name in ("QRME_DB", "QRME_LLM")}
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["QRME_DB"] = str(pathlib.Path(tmp) / "test.db")
        os.environ["QRME_LLM"] = "stub"
        qrme_db.reset()
        try:
            return work()
        finally:
            qrme_db.reset()
            for name, value in kept.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            qrme_db.reset()


def _driving(work):
    """Run `work(client, profile_id, interactor_id)` and count.

    The scene comes from `conftest.make_profile` / `make_interactor` — the
    fixtures' own bodies — because a measure that set its own scene would be
    measuring a different drive than the guard it audits, and the two would
    agree right up until the day the fixture changed.
    """
    def go() -> int:
        from fastapi.testclient import TestClient

        def driven() -> int:
            from qrme.api import create_app
            from .conftest import make_interactor, make_profile
            with TestClient(create_app()) as client:
                return work(client, make_profile(client),
                            make_interactor(client))

        return _in_a_fresh_qrme(driven)
    return go


def _reached(module: str):
    """The bindings one client's drive actually got an answer out of."""
    def work(client, profile_id, interactor_id) -> int:
        from importlib import import_module
        driven = import_module(f".{module}", __package__)._drive(
            client, profile_id, interactor_id)
        return sum(1 for row in driven if row[-1] is not None)
    return _driving(work)


def _bodies_validated() -> int:
    """The body-taking routes the canary sweep got as far as validation on."""
    def work(client, _profile_id, _interactor_id) -> int:
        from .test_the_refusal_that_handed_the_body_back import _sweep
        return _sweep(client)[1]
    return _driving(work)()


def _shortest_refusal() -> int:
    """The shortest sentence the wearables view publishes as a reason.

    `len(why) > 40` read as an exemptible not-a-floor — a length, like a
    status code — and the count guard was right to refuse it. 40 stands for
    "is this a sentence at all", and the sentences these routes publish are
    two hundred characters of explanation. A floor at a fifth of that would
    sit quiet while a reason was cut down to a stub, which is the whole thing
    the screen shows it for.
    """
    def work(client, _profile_id, _interactor_id) -> int:
        from .test_two_questions_a_mark_answers import _owner
        owner, head = _owner(client, "acct_micpub")
        view = client.get(f"/profiles/{owner['id']}/wearables",
                          headers=head).json()
        return min((len(why) for why in view["refusal_reasons"].values()),
                   default=0)
    return _driving(work)()


def _erase_planted() -> int:
    def go():
        from .test_an_erase_is_measured_against_the_schema import plantable
        return plantable()
    return _in_a_fresh_qrme(go)


def _erase_scoped() -> int:
    def go():
        from .test_an_erase_is_measured_against_the_schema import scoped_tables
        return len(scoped_tables())
    return _in_a_fresh_qrme(go)


def _body_routes_count() -> int:
    from qrme.api import app

    from .test_the_refusal_that_handed_the_body_back import _body_routes
    return len(_body_routes(app))


def _capability_tables_count() -> int:
    from .test_termination_revokes_more_than_the_owners_token import (
        _capability_tables)
    return len(_capability_tables())


def _route_shapes() -> int:
    from .test_a_screen_expects_the_shape_the_route_returns import route_shapes
    return len(route_shapes())


def _calls_typed() -> int:
    from .test_a_screen_expects_the_shape_the_route_returns import calls
    return len(calls())


def _guard_names() -> int:
    from .test_the_three_suites_ask_the_same_questions import TESTS, guard_names
    return len(guard_names(TESTS))


def _files_swept() -> int:
    from .test_a_floor_is_within_sight_of_what_it_measures import parsed_files
    return parsed_files()


def _nav_tabs() -> int:
    from .test_nav_labels_are_localised import _nav_ids
    return len(_nav_ids())


def _skin_shelf() -> int:
    from qrme import avatars
    return len(avatars.MARKET)

#: The registry. Every entry replaced a bare literal inside an assertion; the
#: assertion now reads its number from here, which is what takes it out of the
#: unregistered backlog.

def _literal_refusals() -> int:
    """Refusal sentences written as a plain string, as the classifier counts
    them now. The floor is here rather than inside the assertion because a
    number in an assertion is a number nothing compares against what it
    measures — and this one guards the walk that every other refusal check
    is built on."""
    from .test_the_platform_refuses_in_one_language import REPO, _refusals
    return len(_refusals(REPO / "qrme")["literal"])


def _translated_refusals() -> int:
    """Rows in the hand-translated refusal table.

    Its assertion carried a literal 9 while the table held 335 — a floor far
    below what it measures, which answers "is the number satisfied" every run
    and would not notice the table being gutted. Registered so the comparison
    happens rather than being assumed.
    """
    from qrme import i18n
    return len(i18n._REFUSALS)


# -- the shells and the shapes they declare ---------------------------------
#
# The same cluster JIM-mini paid down, measured here rather than assumed from
# there. The prediction in this file's header was that a literal copied into
# three repositories is calibrated for whichever was smallest when it was
# written -- and in this direction it came out the other way round. These
# floors were set locally and most sit at four-fifths already; JIM-mini's
# equivalents had drifted to a third. A number is not stale because it is
# shared; it is stale because nobody measured it.


def _shell_files(kind: str):
    def go() -> int:
        from . import test_the_shells_still_parse as m
        return len(getattr(m, kind))
    return go


def _xaml_named() -> int:
    from .test_the_shells_still_parse import XAML, _XNAME
    return sum(len(set(_XNAME.findall(p.read_text(encoding="utf-8"))))
               for p in XAML)


def _xaml_handlers() -> int:
    from .test_the_shells_still_parse import XAML, _handlers
    return _handlers(XAML)[0]


def _xaml_driveable() -> int:
    from .test_the_shells_still_parse import XAML, _undriveable
    return _undriveable(XAML)[0]


def _swift_structs() -> int:
    from .test_the_shape_the_swift_client_expects import _structs
    return len(_structs())


def _swift_fields() -> int:
    from .test_the_shape_the_swift_client_expects import _structs
    return sum(len(f) for f in _structs().values())


def _swift_bindings() -> int:
    from .test_the_shape_the_swift_client_expects import _bindings
    return len(_bindings())


def _console_shapes() -> int:
    from .test_the_shape_the_console_expects import _shapes
    return len(_shapes())


def _console_shape_fields() -> int:
    from .test_the_shape_the_console_expects import _shapes
    return sum(len(f) for f in _shapes().values())


def _console_gets() -> int:
    from .test_the_shape_the_console_expects import _gets
    return len(_gets())


def _client_bindings() -> int:
    from .test_the_shape_the_client_expects import _bindings
    return len(_bindings())


# -- the readers that stand between a guard and nothing ---------------------
#
# The README pair is the shared-literal case measured for the third time: a
# floor of 40 against 258 history rows here, 256 in JIM-mini and 254 in the
# vault. One number, three products, never revisited in any of them.


def _form_asked_for() -> int:
    from .test_a_form_that_asks_for_it_has_a_label_for_it import _asked_for
    return len(_asked_for())


def _wire_declared() -> int:
    from .test_one_name_one_type_on_the_wire import _declared
    return len(_declared())


def _face_kinds() -> int:
    from qrme import overlays
    return len(overlays.FACE_KINDS)


def _readme_rows() -> int:
    from .test_the_readme_says_what_shipped import _rows
    return len(_rows())


def _readme_released() -> int:
    from .test_the_readme_says_what_shipped import _released
    return len(_released())


def _validation_messages() -> int:
    from qrme import i18n
    return len(i18n._VALIDATION)


# -- the shell translation blocks -------------------------------------------
#
# Ten tests each owned a prefix group and a hand-set floor on it, in ten
# copies of the same twenty lines. `shelltables.py` holds the reader now and
# these hold the numbers.
#
# Worth recording what measuring them found, because it is not what the rest
# of this paydown found: every one was already in band, ratios 0.71 to 1.00,
# three of them exactly at their own count. They keep those floors rather than
# being recomputed to four-fifths — lowering a guard that holds tight to
# satisfy a convention about where floors usually sit would be following the
# rule off a cliff.
#
#     asked     is this floor unregistered
#     mattered  is this floor wrong
#
# The backlog counts the first. It has never counted the second, and the two
# sets overlap less than the shrinking of one suggests about the other.


def _l10n_block(group: str):
    def go() -> int:
        from . import shelltables
        return len(shelltables.ios_keys(group))
    return go


# -- what each receiver declares --------------------------------------------
#
# `RECEIVERS` already carries a floor per receiver, and
# `test_the_scan_reads_every_receiver` uses it — for the *reached* count. The
# line above it floored the *declared* count at a blanket 5, for receivers
# holding between eight and one thousand two hundred and fifty-two members.
#
#     asked     did the scan read this receiver
#     mattered  did it read enough of it to be reading it at all
#
# The number was in the data the whole time; the tuple's own floor sits one
# line below, doing this job for the other half of the check. Two quantities,
# one of them measured per receiver and one of them guessed at once for all of
# them — which is the same defect as a value handed to a function that never
# reads it, and this estate has now found that shape four times in a day.


def _receiver_declared(label: str):
    def go() -> int:
        from . import test_the_member_that_isnt_there as m
        for row in m.RECEIVERS:
            if row[0] == label:
                return len(m._declared(row[1], m.REPO / row[2]))
        raise KeyError(f"no receiver labelled {label!r}")
    return go


# -- the guards on the guards -----------------------------------------------
#
# Every floor below stands under a docstring that says, in its own file's
# words, that a reader which stopped reading would report a clean result. Five
# of them carried the same literal in all three products, and three carried
# some version of the same sentence:
#
#     Thresholds are kept low enough to hold in all three repositories, which
#     have consoles of very different sizes.
#
# This file's header diagnosed that sentence once already — a true sentence
# about why the number is small and a false one about what it holds. It was
# fixed in one file and never carried anywhere else. Twenty against this
# console's 530 bindings is under four per cent.
#
#     asked     does one number hold in all three products
#     mattered  does it hold anything in any of them
#
# Four more sat inside a loop, where one literal has to be four-fifths of
# three surfaces at once and settles for being four-fifths of none. Those are
# registered per surface: this product's Windows shell puts 4,587 literals on
# screens and its iPhone 1,950, under a shared floor of 100.


def _console_bindings() -> int:
    from .test_a_binding_is_not_a_door import _bindings
    return len(_bindings())


def _api_functions(shell: str):
    def go() -> int:
        from .test_a_native_binding_is_not_a_door_either import _api_functions
        return len(_api_functions(shell))
    return go


def _path_segments() -> int:
    from .test_error_report_carries_nothing_private import _segments
    return len(_segments())


def _scanned_controls() -> int:
    from .test_a_form_that_asks_for_it_has_a_label_for_it import (
        _scanned_controls as go)
    return go()


def _egress_sites() -> int:
    from .test_nothing_leaves_the_host import _egress_sites
    return len(_egress_sites())


def _shell_shown(shell: str):
    def go() -> int:
        from .test_a_shell_does_not_print_what_it_translated import (
            SHELLS, _shown)
        return len(_shown(SHELLS[shell]))
    return go


def _shell_fragments(shell: str):
    def go() -> int:
        from .test_a_shell_does_not_print_what_it_translated import (
            SHELLS, _fragments)
        return len(_fragments(SHELLS[shell]))
    return go


def _public_keys() -> int:
    from .test_the_stranger_has_a_language_too import _public_keys
    return len(_public_keys())


def _accountless_chars(shell: str):
    def go() -> int:
        from .test_the_strangers_language_on_a_phone import _accountless_text
        return len(_accountless_text(shell))
    return go


def _plans_threaded() -> int:
    from .test_the_refusal_has_somewhere_to_send_you import _plans_threaded
    return _plans_threaded()


def _key_vocabulary() -> int:
    from .test_the_key_the_server_never_sends import _vocabulary
    return len(_vocabulary())


# -- the floors the sweep was too coarse to see -----------------------------
#
# `SMALLEST_FLOOR` was five, so `assert n >= 2` never entered the backlog. The
# cutoff was right about most of what it hid: a two or a three is usually a
# shape check on a response body, not a floor on a scanned surface. It was
# wrong about these — and measuring them is what retired the cutoff, which the
# sweep now replaces with a question about the expression rather than the
# number.
#
#     asked     is this floor big enough to be worth auditing
#     mattered  is this floor smaller than what it stands over
#
# It filters on the number's size as a stand-in for the number's kind, and
# the stand-in fails in both directions — it would drag in fifty-two runtime
# assertions if it were lowered, and it hides a two standing over a hundred
# and twenty-seven.

def _requests_built(shell: str):
    def go() -> int:
        import re
        from . import test_the_language_nobody_was_sending as m
        for name, _, _, _, client, _ in m.SHELLS:
            if name == shell:
                return len(re.findall(m.BUILT[name], m._code(m.REPO / client)))
        raise KeyError(f"no shell named {shell!r}")
    return go


def _ratchet_files() -> int:
    from .test_a_record_that_outlived_the_code import _ratchets
    return len(_ratchets())


def _backup_git_calls() -> int:
    """The git invocations the backup scripts build, run against a scratch
    repository so a flag git does not have fails in the suite."""
    from .test_a_flag_the_tool_does_not_have import _calls
    return len(_calls())


def _readme_files() -> int:
    from .test_readme_scripture import _readmes
    return len(_readmes())


def _verbs_min() -> int:
    """The fewest distinct verbs any one surface reports.

    A minimum rather than a total, because the assertion runs per surface: a
    floor on the sum would be satisfied by one surface reading well while
    another had gone silent.
    """
    from .test_native_routes_exist import NATIVE, calls
    return min(len({method for method, _ in calls(lang)})
               for lang in NATIVE)


def _thinnest_closure() -> int:
    from .test_a_profile_has_no_hands_on_the_money import AUTONOMOUS, _closure
    return min(len(_closure(root)) for root in AUTONOMOUS)


def _gallery_tables() -> int:
    from .test_the_gallery_is_a_grid import _galleries
    return len(list(_galleries()))


def _workflow_files() -> int:
    from .test_a_check_that_cannot_fail_before_the_merge import _files
    return len(_files())


# -- the floors that were already holding ----------------------------------
#
# The other half of what widening the sweep turned up, and the half that is
# easy to leave alone: measured, in band, several at exactly the number they
# stand over. Nothing here is being corrected.
#
#     asked     is this floor wrong
#     mattered  is anything comparing it to what it measures
#
# A floor at 1.00 today is a floor at 0.30 in a year, and the run it starts
# being wrong on is a run nobody watches. What registering buys one that
# holds is not a different number — it is the measurement attached, and the
# audit every run. Each keeps the number it had unless four-fifths of what it
# measures is higher, because lowering a guard that currently holds tight, to
# satisfy a convention about where floors usually sit, is following the rule
# off a cliff.


def _template_calls() -> int:
    from .test_a_refusal_whose_english_is_not_a_constant import _template_calls
    return len(_template_calls())


def _deploy_check_blocks() -> int:
    from .test_the_deploy_page_is_paste_ready import _checks
    return len(_checks())


def _generating_routes() -> int:
    from .test_a_memorial_does_not_keep_posting import _generating_routes
    return len(_generating_routes())


def _form_declared_fields() -> int:
    from .test_the_refusal_names_the_field_on_the_form import _declared
    return len(_declared())


def _android_reads() -> int:
    from .test_the_keys_the_android_client_reads import _reads
    return len(_reads())


def _android_read_keychars() -> int:
    from .test_the_keys_the_android_client_reads import _reads
    return sum(len(k) for _, k in _reads())


def _nav_keys() -> int:
    from .test_the_nav_is_translated_and_nothing_behind_it_is import _nav_keys
    return len(_nav_keys())


def _nav_entries() -> int:
    from .test_the_nav_is_translated_and_nothing_behind_it_is import _nav_ids
    return len(_nav_ids())


def _record_wire_names() -> int:
    from .test_the_shape_the_client_expects import _records
    return len({wire for fields in _records().values() for wire, _ in fields})


def _route_writes() -> int:
    from .test_the_body_the_route_requires import WRITES, _sent
    return len([w for w in _sent() if w[0] in WRITES])


def _route_writes_readable() -> int:
    from .test_the_body_the_route_requires import WRITES, _sent
    return len([w for w in _sent() if w[0] in WRITES
                and w[2] in ("literal", "parameter") and w[3] is not None])


def _route_models() -> int:
    from .test_the_body_the_route_requires import _models
    return len(_models())


def _route_writes_meeting_a_model() -> int:
    from .test_the_body_the_route_requires import _writes_meeting_a_model
    return _writes_meeting_a_model()


def _body_matched(slug: str):
    def go() -> int:
        from . import test_the_body_the_native_clients_send as m
        for client, short in m.SLUG.items():
            if short == slug:
                return m._writes_meeting_a_model(client)
        raise KeyError(f"no native client slugged {slug!r}")
    return go


def _shell_sources(shell: str):
    def go() -> int:
        from .test_the_files_the_release_never_touched import _shell_sources
        return len(_shell_sources(shell))
    return go


def _capability_used(shell: str):
    def go() -> int:
        from . import test_the_files_the_release_never_touched as m
        needs = m.IOS_NEEDS if shell == "ios" else m.ANDROID_NEEDS
        return len(m._used(m._shell_sources(shell), needs))
    return go


def _inside_count(needle: str):
    def go() -> int:
        from .test_the_room_speaks_for_itself import INSIDE
        return INSIDE.count(needle)
    return go


def _l10n_sentences(needle: str):
    def go() -> int:
        from .test_a_code_on_a_wall import _markup
        return _markup("app/src/l10n.ts").count(needle)
    return go


def _close_reasons() -> int:
    from . import test_the_conversation_leaves_the_application as m
    import re
    found = re.search(
        r"override fun onError\(code: Int\)\s*\{(.*?)\n            \}",
        m.SERVICE.read_text(encoding="utf-8"), re.S)
    return found.group(1).count("close(reason =") if found else 0


def _build_steps() -> int:
    from .test_the_installer_can_actually_report import _build_steps
    return len(_build_steps())


def _exception_handlers() -> int:
    from .test_the_platform_refuses_in_one_language import _handlers
    return len(_handlers())


def _brushes(half: int):
    def go() -> int:
        from .test_the_member_that_isnt_there import _brushes
        return len(_brushes()[half])
    return go


def _console_request_headers() -> int:
    from .test_the_language_nobody_was_sending import _console_headers
    return len(_console_headers())


def _governance_handlers() -> int:
    from .test_the_objector_cannot_read_their_own_case import _route_handlers
    return len(_route_handlers())


def _starter_industries() -> int:
    from .test_starter_profiles import STARTERS
    return len({industry for _h, industry, *_ in STARTERS})


def _thinnest_pack() -> int:
    from .test_knowledge_packs import STARTER_PACKS
    return min(len(items) for _title, items in STARTER_PACKS.values())


def _degrading_wrappers() -> int:
    from .test_the_provenance_names_who_answered import _degrading_wrappers
    return len(_degrading_wrappers())


def _real_providers() -> int:
    """Registry rows with a home country — the menu the region loadouts
    curate from. Local and self-supplied rows are offered everywhere and
    are not what "at least eight providers" was asking about."""
    from qrme import llm
    return sum(1 for spec in llm._REGISTRY.values()
               if spec.get("origin") not in ("local", "any"))


def _wheel_declared() -> int:
    from .test_the_image_holds_what_the_wheel_declares import _declared
    return len(_declared())


def _console_players() -> int:
    from .test_a_player_handed_no_origin_will_not_play import _players
    return len(_players())


def _answer_pieces() -> int:
    from .test_the_answer_begins_before_it_ends import LONG_ANSWER, _pieces
    return len(_pieces(LONG_ANSWER)[0])


def _thinnest_pin() -> int:
    from .test_the_shape_inside_the_shape import contract, _pin_rows
    return min(len(contract(*row)) for row in _pin_rows())


# -- the floors the parametrize hid -----------------------------------------
#
# Every one of these sat inside a `@pytest.mark.parametrize("shell", ...)`,
# which is the same defect as a literal under a loop wearing pytest's
# clothes: one number standing for three shells, calibrated for none of
# them, and invisible to the replay harness because the name `shell` only
# exists while pytest is running.
#
# The sharpest fossil: a docstring reading "QRME's Windows shell makes
# exactly two localizer calls — the nav loop and one button". It makes
# 1,278 now. The floor of 2 under it was two tenths of one per cent of the
# surface it claimed to hold, under a sentence that had been precisely true
# the day it was written.


def _screens_declared(shell: str):
    def go() -> int:
        from .test_a_screen_nothing_opens import _declared
        return len(_declared(shell))
    return go


def _screens_localizer_calls(shell: str):
    def go() -> int:
        from .test_a_screen_nothing_opens import _call_sites
        return len(_call_sites(shell))
    return go


def _room_format_guards() -> int:
    """How many storage accesses in `roomFormat.ts` are inside a try.

    Every read and every write of `localStorage` has to be caught: a
    private window, cleared site data or a browser set to block storage
    make the access itself raise, and a screen that cannot remember the
    viewer's chosen format still has to draw the room.

    Counted rather than asserted at a literal 2, because the number is a
    property of the module — it moves when a third access is added, and a
    floor that does not move with it stops measuring anything.
    """
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    text = (root / "app" / "src" / "roomFormat.ts").read_text(encoding="utf-8")
    return text.count("try {")


def _problems_recorded(shell: str):
    def go() -> int:
        from .test_native_shells_record_nothing_private import _record_calls
        return len(_record_calls(shell))
    return go


def _tabs_onscreen(shell: str):
    def go() -> int:
        from .test_the_tabs_are_translated_and_the_screens_are_not import (
            _measure)
        english, calls = _measure(shell)
        return english + calls
    return go


def _tabs_localizer_calls(shell: str):
    def go() -> int:
        from .test_the_tabs_are_translated_and_the_screens_are_not import (
            _measure)
        return _measure(shell)[1]
    return go


def _tabs_table_rows(shell: str):
    def go() -> int:
        from .test_the_tabs_are_translated_and_the_screens_are_not import (
            _rows)
        return len(_rows(shell))
    return go


def _shared_with_console(shell: str):
    def go() -> int:
        from .test_the_desktop_and_the_phone_say_different_things import (
            _shared_with_console)
        return len(_shared_with_console(shell))
    return go


def _shellstable_rows(shell: str):
    def go() -> int:
        from .test_the_shells_table_answers_every_reader import _rows
        return len(_rows(shell))
    return go


def _pool_positions() -> int:
    from qrme import occupations
    return occupations.count()


def _pool_families() -> int:
    from qrme import occupations
    return len(occupations.families())


RATCHETS: tuple[Ratchet, ...] = (
    Ratchet("screens.declared.android", 13, _screens_declared("android"),
            "the screens android declares, as the navigation scan reads them"),
    Ratchet("screens.declared.ios", 67, _screens_declared("ios"),
            "the screens ios declares, as the navigation scan reads them"),
    Ratchet("screens.declared.windows", 17, _screens_declared("windows"),
            "the screens windows declares, as the navigation scan reads them"),
    Ratchet("screens.localizer_calls.android", 860, _screens_localizer_calls("android"),
            "the localizer call sites the android screen scan finds"),
    Ratchet("screens.localizer_calls.ios", 996, _screens_localizer_calls("ios"),
            "the localizer call sites the ios screen scan finds"),
    Ratchet("screens.localizer_calls.windows", 1022, _screens_localizer_calls("windows"),
            "the localizer call sites the windows screen scan finds"),
    Ratchet("problems.recorded.android", 4, _problems_recorded("android"),
            "the failure kinds android's client records — the refusal and the never-reached case"),
    Ratchet("problems.recorded.ios", 3, _problems_recorded("ios"),
            "the failure kinds ios's client records — the refusal and the never-reached case"),
    Ratchet("problems.recorded.windows", 3, _problems_recorded("windows"),
            "the failure kinds windows's client records — the refusal and the never-reached case"),
    Ratchet("tabs.onscreen.android", 860, _tabs_onscreen("android"),
            "the on-screen strings the android extraction reads"),
    Ratchet("tabs.onscreen.ios", 996, _tabs_onscreen("ios"),
            "the on-screen strings the ios extraction reads"),
    Ratchet("tabs.onscreen.windows", 1022, _tabs_onscreen("windows"),
            "the on-screen strings the windows extraction reads"),
    Ratchet("tabs.localizer_calls.android", 860, _tabs_localizer_calls("android"),
            "the localizer calls the android tabs scan finds"),
    Ratchet("tabs.localizer_calls.ios", 996, _tabs_localizer_calls("ios"),
            "the localizer calls the ios tabs scan finds"),
    Ratchet("tabs.localizer_calls.windows", 1022, _tabs_localizer_calls("windows"),
            "the localizer calls the windows tabs scan finds"),
    Ratchet("tabs.table_rows.android", 1078, _tabs_table_rows("android"),
            "the rows the android table parser reads"),
    Ratchet("tabs.table_rows.ios", 1056, _tabs_table_rows("ios"),
            "the rows the ios table parser reads"),
    Ratchet("tabs.table_rows.windows", 1052, _tabs_table_rows("windows"),
            "the rows the windows table parser reads"),
    Ratchet("table.shared_with_console.android", 392, _shared_with_console("android"),
            "the English strings android's table shares with the console"),
    Ratchet("table.shared_with_console.ios", 397, _shared_with_console("ios"),
            "the English strings ios's table shares with the console"),
    Ratchet("table.shared_with_console.windows", 392, _shared_with_console("windows"),
            "the English strings windows's table shares with the console"),
    Ratchet("shellstable.rows.android", 1078, _shellstable_rows("android"),
            "the rows the android shell-table scan parses"),
    Ratchet("shellstable.rows.ios", 1056, _shellstable_rows("ios"),
            "the rows the ios shell-table scan parses"),
    Ratchet("shellstable.rows.windows", 1052, _shellstable_rows("windows"),
            "the rows the windows shell-table scan parses"),
    Ratchet("refusals.template_calls", 152, _template_calls,
            "the `i18n.fill` call sites the conversion left behind"),
    Ratchet("deploy.check_blocks", 2, _deploy_check_blocks,
            "the check blocks the deploy page offers a choice between"),
    Ratchet("route.generating", 10, _generating_routes,
            "the routes that generate, as the walk finds them"),
    Ratchet("form.declared_fields", 256, _form_declared_fields,
            "the request-model fields the refusal check maps to a control"),
    Ratchet("android.reads", 175, _android_reads,
            "the key reads the Android extractor finds"),
    Ratchet("android.read_keychars", 417, _android_read_keychars,
            "the characters across those keys, as a shape check on them"),
    Ratchet("console.nav_keys", 44, _nav_keys,
            "the `nav.*` rows the console's table declares"),
    Ratchet("console.nav_entries", 44, _nav_entries,
            "the tab ids `App.tsx` declares"),
    Ratchet("console.record_wire_names", 518, _record_wire_names,
            "the wire names the record-aware client extractor reads"),
    Ratchet("route.writes", 195, _route_writes,
            "the write calls the extractor reads off the clients"),
    Ratchet("route.writes_readable", 158, _route_writes_readable,
            "the write calls whose body it can actually read"),
    Ratchet("route.models", 162, _route_models,
            "the request models FastAPI publishes in the schema"),
    Ratchet("route.writes_meeting_a_model", 156, _route_writes_meeting_a_model,
            "the clients' writes whose verb and shape meet a model"),
    Ratchet("native.body_matched.windows", 160, _body_matched("windows"),
            "the desktop client's writes that meet a declared model"),
    Ratchet("native.body_matched.ios", 158, _body_matched("ios"),
            "the iPhone client's writes that meet a declared model"),
    Ratchet("native.body_matched.android", 158, _body_matched("android"),
            "the Android client's writes that meet a declared model"),
    Ratchet("shell.sources.ios", 40, _shell_sources("ios"),
            "the Swift sources the release check walks"),
    Ratchet("shell.sources.android", 10, _shell_sources("android"),
            "the Kotlin sources the release check walks"),
    Ratchet("capability.used.ios", 3, _capability_used("ios"),
            "the gated iPhone capabilities the shell actually calls"),
    Ratchet("capability.used.android", 2, _capability_used("android"),
            "the gated Android capabilities the shell actually calls"),
    Ratchet("room.voicing_cleared", 3, _inside_count("setVoicing(null)"),
            "the places the room stops showing a voice as speaking"),
    Ratchet("room.talking_checks", 3, _inside_count("isTalking(s)"),
            "the places the room asks whether a speaker is talking"),
    Ratchet("l10n.scan_sentences", 2, _l10n_sentences("counts as a scan"),
            "the translated sentences saying what counts as a scan"),
    Ratchet("l10n.press_sentences", 2, _l10n_sentences("pressed a button"),
            "the translated sentences saying a button was pressed"),
    Ratchet("service.close_reasons", 3, _close_reasons,
            "the ways the listening service says why it stopped"),
    Ratchet("installer.build_steps", 3, _build_steps,
            "the steps that run the packaging command"),
    Ratchet("api.exception_handlers", 2, _exception_handlers,
            "the exception handlers `api.py` declares"),
    Ratchet("brush.keys", 16, _brushes(0),
            "the brush keys App.xaml declares"),
    Ratchet("brush.used", 10, _brushes(1),
            "the brush keys the screens actually paint with"),
    Ratchet("console.request_headers", 3, _console_request_headers,
            "the headers the console attaches to every request"),
    Ratchet("governance.route_handlers", 8, _governance_handlers,
            "the route handlers the governance walk parses"),
    Ratchet("starters.industries", 30, _starter_industries,
            "the industries the starter profiles cover"),
    Ratchet("packs.thinnest", 3, _thinnest_pack,
            "the items in the thinnest starter pack"),
    Ratchet("degrading.wrappers", 2, _degrading_wrappers,
            "the wrappers that degrade quietly, as the walk finds them"),
    Ratchet("llm.real_providers", 12, _real_providers,
            "the providers on the model menu with a home country"),
    Ratchet("wheel.declared", 2, _wheel_declared,
            "the variables the deploy wheel declares"),
    Ratchet("console.players", 2, _console_players,
            "the players the console mounts"),
    Ratchet("speech.pieces_from_a_long_answer", 2, _answer_pieces,
            "the pieces a long answer splits into before it is spoken"),
    Ratchet("pin.thinnest", 2, _thinnest_pin,
            "the keys on the thinnest pinned contract"),
    # Per shell, and the reason is in the numbers: this one literal stood
    # over 10, 8 and 123 requests built. It was honest about the
    # iPhone and decoration on the desktop, which is what a single floor
    # under a loop over three surfaces always ends up being.
    Ratchet("language.requests_built.ios", 8, _requests_built("ios"),
            "the requests the iPhone client builds"),
    Ratchet("language.requests_built.android", 6, _requests_built("android"),
            "the requests the Android client builds"),
    Ratchet("language.requests_built.windows", 98, _requests_built("windows"),
            "the requests the desktop client builds"),
    Ratchet("autonomy.thinnest_closure", 11, _thinnest_closure,
            "the siblings the thinnest autonomous root imports"),
    Ratchet("ratchet.files", 20, _ratchet_files,
            "the ratchet records this suite keeps"),
    Ratchet("gallery.tables", 24, _gallery_tables,
            "the gallery tables the README carries. It was fifteen until "
            "the round that photographs a screen whole: a screen taller "
            "than the glass is also sliced a phone height at a time, and "
            "each long screen's slices are a table of their own"),
    Ratchet("route.verbs_min", 4, _verbs_min,
            "the distinct verbs the thinnest-reading shell reports"),
    Ratchet("backup.git_calls", 5, _backup_git_calls,
            "the git invocations the backup scripts build"),
    Ratchet("readme.files", 7, _readme_files,
            "the READMEs the passage check reads"),
    Ratchet("workflow.files", 5, _workflow_files,
            "the workflow files the gating sweep reads"),
    Ratchet("console.bindings_scanned", 424, _console_bindings,
            "the bindings the console scan parses out of api.ts"),
    Ratchet("native.api_functions.ios", 438, _api_functions("ios"),
            "the calls the iPhone's ApiClient declares"),
    Ratchet("route.path_segments", 284, _path_segments,
            "the literal path segments this product's routes contribute"),
    Ratchet("form.controls_scanned", 21466, _scanned_controls,
            "the characters of form control the screen scan matches"),
    # 20, not 12. The floor had drifted to less than half of what it
    # measures — 25 calls could have fallen to 12 without a word — and
    # adding the converter's one call to the forge is what tipped the
    # guard over. Four-fifths of the real count, which is what
    # `test_no_registered_floor_is_decoration` asks of every floor here.
    Ratchet("host.egress_sites", 20, _egress_sites,
            "the calls in this package that can put bytes on a wire"),
    Ratchet("shell.shown.ios", 1560, _shell_shown("ios"),
            "the literals the iOS scan finds on any screen"),
    Ratchet("shell.shown.android", 1133, _shell_shown("android"),
            "the literals the Android scan finds on any screen"),
    Ratchet("shell.shown.windows", 3669, _shell_shown("windows"),
            "the literals the Windows scan finds on any screen"),
    Ratchet("shell.fragments.ios", 56, _shell_fragments("ios"),
            "the fragments split out of the iOS table's slotted rows"),
    Ratchet("shell.fragments.android", 57, _shell_fragments("android"),
            "the fragments split out of the Android table's slotted rows"),
    Ratchet("shell.fragments.windows", 58, _shell_fragments("windows"),
            "the fragments split out of the Windows table's slotted rows"),
    Ratchet("console.public_keys", 101, _public_keys,
            "the console's translations for somebody with no account"),
    Ratchet("accountless.screen_chars.ios", 9771, _accountless_chars("ios"),
            "the characters the iPhone's accountless screen reads as"),
    Ratchet("accountless.screen_chars.android", 8708,
            _accountless_chars("android"),
            "the characters Android's accountless screen reads as"),
    Ratchet("accountless.screen_chars.windows", 13636,
            _accountless_chars("windows"),
            "the characters the desktop's accountless screen reads as"),
    Ratchet("console.plans_threaded", 35, _plans_threaded,
            "the screens the shell hands a way out of a plan gate"),
    Ratchet("key.vocabulary", 2229, _key_vocabulary,
            "the field names the leak check knows to look for"),
    Ratchet("receiver.declared.ios.state", 16, _receiver_declared("ios/state"),
            "the members ios/state declares"),
    Ratchet("receiver.declared.ios.api", 1026, _receiver_declared("ios/api"),
            "the members ios/api declares"),
    Ratchet("receiver.declared.ios.theme", 12, _receiver_declared("ios/theme"),
            "the members ios/theme declares"),
    Ratchet("receiver.declared.android.state", 17, _receiver_declared("android/state"),
            "the members android/state declares"),
    Ratchet("receiver.declared.android.api", 958, _receiver_declared("android/api"),
            "the members android/api declares"),
    Ratchet("receiver.declared.android.theme", 14, _receiver_declared("android/theme"),
            "the members android/theme declares"),
    Ratchet("receiver.declared.windows.state", 15, _receiver_declared("windows/state"),
            "the members windows/state declares"),
    Ratchet("receiver.declared.windows.api", 768, _receiver_declared("windows/api"),
            "the members windows/api declares"),
    Ratchet("l10n.block.lobby", 45, _l10n_block("lobby"),
            "the bot/refer/object/lobby/dock keys the iOS table carries"),
    Ratchet("l10n.block.crowd", 45, _l10n_block("crowd"),
            "the crowd/party/lend keys the iOS table carries"),
    Ratchet("l10n.block.face", 43, _l10n_block("face"),
            "the avatar, emblem and steering keys the iOS table carries"),
    # 40 -> 38 in the dead-keys close: acct.reset.code and life.legend were
    # held by all three shells and asked for by none — see
    # native_dead_keys.txt, 1.8.5.
    Ratchet("l10n.block.till", 38, _l10n_block("till"),
            "the acct/till/life keys the iOS table carries"),
    Ratchet("l10n.block.lastdoors", 42, _l10n_block("lastdoors"),
            "the born/mind/reach/lic/sens keys the iOS table carries"),
    Ratchet("l10n.block.place", 44, _l10n_block("place"),
            "the place/cam/org/tut keys the iOS table carries"),
    Ratchet("l10n.block.record", 40, _l10n_block("record"),
            "the memory, source and exit keys the iOS table carries"),
    Ratchet("l10n.block.seal", 46, _l10n_block("seal"),
            "the signature, mail and room keys the iOS table carries"),
    Ratchet("l10n.block.sticker", 34, _l10n_block("sticker"),
            "the beacon, queue and stamp keys the iOS table carries"),
    # 49 -> 47: work.phase, task.gid and task.list left in the same close.
    # Three rows out against a floor that moved by two — the measured count
    # had sat one above the floor since the block was ratcheted.
    Ratchet("l10n.block.workshop", 47, _l10n_block("workshop"),
            "the workflow, delegation and task keys the iOS table carries"),
    Ratchet("form.asked_for", 44, _form_asked_for,
            "the request fields the form check knows a control for"),
    Ratchet("wire.declared", 524, _wire_declared,
            "every name declared on the wire, across all four clients"),
    Ratchet("overlays.face_kinds", 13, _face_kinds,
            "the face kinds an overlay can be drawn for"),
    Ratchet("readme.history_rows", 206, _readme_rows,
            "the release history rows the README table carries"),
    Ratchet("readme.released", 208, _readme_released,
            "the releases the CHANGELOG declares"),
    Ratchet("i18n.validation_messages", 8, _validation_messages,
            "the validation sentences with a row in every language"),
    Ratchet("shells.swift_files", 39, _shell_files("SWIFT"),
            "the Swift sources the shell parser reads"),
    Ratchet("shells.kotlin_files", 9, _shell_files("KOTLIN"),
            "the Kotlin sources the shell parser reads"),
    Ratchet("shells.csharp_files", 23, _shell_files("CSHARP"),
            "the C# sources the shell parser reads"),
    Ratchet("shells.xaml_files", 19, _shell_files("XAML"),
            "the XAML screens the markup checks reach"),
    Ratchet("shells.xaml_named", 1047, _xaml_named,
            "the named elements across those XAML screens"),
    Ratchet("shells.xaml_handlers", 387, _xaml_handlers,
            "the XAML handlers checked against their code-behind"),
    Ratchet("shells.xaml_driveable", 916, _xaml_driveable,
            "the XAML elements the drive check reaches"),
    Ratchet("swift.structs", 266, _swift_structs,
            "the Swift client's declared shapes"),
    Ratchet("swift.struct_fields", 1027, _swift_fields,
            "the fields across the Swift client's shapes"),
    Ratchet("swift.bindings", 212, _swift_bindings,
            "the Swift screens' bindings to those shapes"),
    Ratchet("console.shapes", 227, _console_shapes,
            "the console's declared shapes"),
    Ratchet("console.shape_fields", 1572, _console_shape_fields,
            "the fields across the console's shapes"),
    Ratchet("console.gets", 191, _console_gets,
            "the console's read calls"),
    Ratchet("console.bindings", 158, _client_bindings,
            "the console screens' bindings to route shapes"),
    Ratchet("refusals.translated", 335, _translated_refusals,
            "rows in the hand-translated refusal table"),
    Ratchet("refusals.literal", 200, _literal_refusals,
            "refusals written as a plain string — the walk every other\n            refusal check stands on"),
    Ratchet("l10n.asked.ios", 760, _l10n("ios", "asked"),
            "screens on the iPhone that call the localizer"),
    Ratchet("l10n.asked.android", 760, _l10n("android", "asked"),
            "screens on Android that call the localizer"),
    Ratchet("l10n.asked.windows", 750, _l10n("windows", "asked"),
            "screens on the desktop that call the localizer"),
    Ratchet("l10n.held.ios", 860, _l10n("ios", "held"),
            "rows in the iPhone's own L10n table"),
    Ratchet("l10n.held.android", 890, _l10n("android", "held"),
            "rows in Android's own L10n table"),
    Ratchet("l10n.held.windows", 880, _l10n("windows", "held"),
            "rows in the desktop's own L10n table"),
    Ratchet("occupations.positions", 45000, _pool_positions,
            "positions the app carries without a model or a network"),
    Ratchet("occupations.families", 16, _pool_families,
            "families a founder can browse the pool by"),
    Ratchet("route.calls.console", 340, _calls("console"),
            "call sites the route audit reads out of the console"),
    Ratchet("route.calls.ios", 340, _calls("ios"),
            "call sites the route audit reads out of the iPhone shell"),
    Ratchet("route.calls.android", 340, _calls("android"),
            "call sites the route audit reads out of the Android shell"),
    Ratchet("route.calls.windows", 340, _calls("windows"),
            "call sites the route audit reads out of the desktop shell"),
    Ratchet("route.table", 380, _route_table,
            "routes reachable by walking the included routers"),
    Ratchet("extractor.path_literals", 1120, _path_literals,
            "path literals found across all four surfaces"),
    Ratchet("console.source_files", 84, _console_files,
            "TypeScript sources the console sink sweep reads"),
    Ratchet("console.calls_typed", 340, _calls_typed,
            "console calls that declare the shape they expect back"),
    Ratchet("refusals.shortest_reason", 165, _shortest_refusal,
            "the shortest sentence the wearables view publishes as a reason"),
    Ratchet("swift.driven", 46,
            _reached("test_the_shape_the_swift_client_expects"),
            "the Swift bindings the shape drive gets an answer out of"),
    Ratchet("windows.driven", 58,
            _reached("test_the_shape_the_client_expects"),
            "the Windows records the shape drive gets an answer out of"),
    Ratchet("console.driven", 74,
            _reached("test_the_shape_the_console_expects"),
            "the console read calls the shape drive gets an answer out of"),
    Ratchet("android.driven", 83,
            _reached("test_the_keys_the_android_client_reads"),
            "the Android reads the key drive gets an answer out of"),
    Ratchet("routes.body_validated", 144, _bodies_validated,
            "the body-taking routes the canary sweep reaches validation on"),
    Ratchet("erase.tables_planted", 59, _erase_planted,
            "tables this suite can put a probe row into"),
    Ratchet("erase.scoped_tables", 69, _erase_scoped,
            "tables the schema scopes to a single profile"),
    Ratchet("erase.capability_tables", 7, _capability_tables_count,
            "profile-scoped tables carrying a revocation flag or a live "
            "token — what termination must reach"),
    Ratchet("routes.body_taking", 210, _body_routes_count,
            "routes that read a request body, as the refusal sweep fills "
            "their paths"),
    Ratchet("route.declared_shapes", 350, _route_shapes,
            "routes whose answer is decisively a list or an object"),
    Ratchet("markup.strings_scanned", 16, _markup_strings,
            "f-strings in this package that build markup"),
    # 3040 against 3804 — four-fifths, which is what the floor guard next
    # door asks of every ratchet here. It sat at 1900 while the suite
    # doubled past it, so half the tests could have disappeared without
    # a word. A floor that cannot notice its own subject leaving is
    # decoration.
    Ratchet("suite.guard_names", 3040, _guard_names,
            "test functions this suite declares"),
    Ratchet("sweep.files_parsed", 280, _files_swept,
            "test files the bare-floor sweep can read"),
    # 40 against 51, not the 20 this was first written with. That 20 came
    # from the sibling product, where it is four-fifths of a 24-tab console
    # and honest — and here it was two-fifths, which is this file's own
    # opening example of a floor that ages into decoration. One number
    # written to work in three repositories is a number calibrated for
    # whichever of them was smallest when it was written.
    Ratchet("console.nav_tabs", 40, _nav_tabs,
            "tabs the console navigation declares — the floor under the "
            "check that every one of them has a label"),
    Ratchet("console.room_format_guards", 2, _room_format_guards,
            "storage accesses in roomFormat.ts wrapped in a try — the floor "
            "under the check that a browser blocking storage cannot take the "
            "room down with it"),
    Ratchet("avatars.skin_shelf", 12, _skin_shelf,
            "systems a face can be imported from — the floor under the "
            "check that a source picker is picking between things"),
)

_BY_NAME = {r.name: r for r in RATCHETS}


def floor(name: str) -> int:
    """The registered floor, by name.

    Assertions call this instead of carrying a literal. A name that is not
    registered is a mistake worth failing on rather than defaulting past — a
    silent default here would be a floor of nothing, which is the whole
    subject of this file.
    """
    try:
        return _BY_NAME[name].floor
    except KeyError:
        raise KeyError(
            f"no ratchet named {name!r}; registered: "
            + ", ".join(sorted(_BY_NAME))) from None
