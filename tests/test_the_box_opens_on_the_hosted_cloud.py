"""The assistant's box opens on the hosted cloud — and by exactly this much.

JIM's coding assistant tries a drafted edit inside user, mount, network and
pid namespaces (jim/workroom.py in the JIM-mini repository). Docker's default
seccomp profile refuses `unshare` and `mount` to a container without
CAP_SYS_ADMIN and its default AppArmor profile denies every mount, so on a
stock box the probe fails and the Studio shows a sentence.

The compose stack answers with two profiles for the jim service only. What
this guard holds is the *only*: each profile is Docker's default plus the
calls the box needs and nothing more, the compose file names both on jim
and on no other service, the script that loads the AppArmor half into the
host's kernel exists and is what the deploy page runs before every `up`.

    asked     can the box open on the hosted cloud
    mattered  did opening it loosen anything else
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
COMPOSE = REPO / "docker" / "beta-compose.yml"
SECCOMP = REPO / "docker" / "jim-box.seccomp.json"
APPARMOR = REPO / "docker" / "jim-box.apparmor"
INSTALL = REPO / "docker" / "jim-box-install.sh"
PAGE = REPO / "docs" / "beta-deploy.md"

#: What the box needs past Docker's default seccomp profile, and nothing else.
NEEDED = {"unshare", "mount", "umount2", "fsopen", "fsconfig", "fsmount",
          "fspick", "move_mount", "open_tree", "mount_setattr"}
#: A few of the calls Docker's default keeps behind CAP_SYS_ADMIN or refuses
#: outright; the widened profile must still.
STILL_HELD = {"reboot", "kexec_load", "init_module", "finit_module",
              "delete_module", "setns", "pivot_root", "swapon", "swapoff",
              "bpf", "perf_event_open", "ptrace"}


def _compose() -> dict:
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


def test_the_compose_file_names_both_profiles_on_jim_and_nowhere_else():
    doc = _compose()
    jim = doc["services"]["jim"]
    opts = jim.get("security_opt") or []
    assert "seccomp=./jim-box.seccomp.json" in opts, opts
    assert "apparmor=jim-box" in opts, opts
    assert (COMPOSE.parent / "jim-box.seccomp.json").is_file()
    for name, svc in doc["services"].items():
        if name == "jim":
            continue
        assert not (svc.get("security_opt")), (
            f"{name} carries a security_opt; the box's profiles are jim's alone")
        assert not svc.get("privileged"), name


def test_the_seccomp_profile_is_dockers_default_plus_the_box_and_nothing_more():
    prof = json.loads(SECCOMP.read_text(encoding="utf-8"))
    assert prof["defaultAction"] == "SCMP_ACT_ERRNO"
    assert prof.get("archMap"), "the default profile's architecture map is gone"
    # Every syscall the box needs is allowed without a capability.
    free = set()
    for group in prof["syscalls"]:
        if group.get("action") == "SCMP_ACT_ALLOW" and not group.get("includes") \
                and not group.get("args"):
            free |= set(group["names"])
    assert NEEDED <= free, sorted(NEEDED - free)
    # And the ones Docker keeps held are still held.
    assert not (STILL_HELD & free), sorted(STILL_HELD & free)
    # The widening is one group, and it says what it is for.
    ours = [g for g in prof["syscalls"] if set(g["names"]) == NEEDED]
    assert len(ours) == 1 and "workroom" in ours[0].get("comment", "")


def test_the_apparmor_profile_is_dockers_default_plus_the_box_and_nothing_more():
    raw = APPARMOR.read_text(encoding="utf-8")
    # The rules, not the commentary about them.
    text = "\n".join(re.sub(r"#(?!include).*", "", ln) for ln in raw.splitlines())
    assert re.search(r"^profile jim-box flags=\(attach_disconnected,mediate_deleted\) \{", text, re.M)
    assert re.search(r"^abi <abi/4\.0>,", text, re.M)
    assert re.search(r"^  userns,", text, re.M)
    assert re.search(r"^  mount,", text, re.M)
    assert "deny mount," not in text
    # The default's denials are kept verbatim.
    for kept in ("deny @{PROC}/sysrq-trigger rwklx,", "deny @{PROC}/kcore rwklx,",
                 "deny /sys/firmware/** rwklx,", "deny /sys/kernel/security/** rwklx,",
                 "deny network alg,", "deny network vsock,",
                 "ptrace (trace,tracedby,read,readby) peer=\"jim-box\",",
                 "signal (send,receive) peer=\"jim-box\","):
        assert kept in text, kept
    # The profile confines this container and no other name.
    assert "docker-default" not in text


def test_the_installer_loads_the_profile_and_survives_an_older_parser():
    text = INSTALL.read_text(encoding="utf-8")
    assert text.startswith("#!/bin/sh")
    assert INSTALL.stat().st_mode & 0o111, "the installer is not executable"
    assert "apparmor_parser -r" in text
    assert "/etc/apparmor.d/jim-box" in text
    assert "jim-box.apparmor" in text
    # An older parser gets the profile without the two AppArmor 4 lines.
    assert "^abi <abi/4.0>," in text and "^  userns," in text
    # A host without AppArmor is told so and left alone, not failed.
    assert "exit 0" in text and "nothing to load" in text


def test_the_deploy_page_runs_the_installer_before_every_up():
    text = PAGE.read_text(encoding="utf-8")
    start = text.index("## 7. Updating a running beta")
    section = text[start:text.index("\n## ", start + 1)]
    block = next(b for b in re.findall(r"```bash\n(.*?)```", section, re.S)
                 if "docker compose" in b and "up -d --build" in b)
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    install = next(i for i, ln in enumerate(lines) if "jim-box-install.sh" in ln)
    up = next(i for i, ln in enumerate(lines) if "up -d --build" in ln)
    assert install < up, "the installer runs after the up; a container named for a profile the kernel does not hold will not start"
    assert "### The assistant's box (3.1.0)" in text
