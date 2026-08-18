"""`available` on the studio agent means somebody real answers.

`llm.available()` is the provider catalog — nine rows, configured or not —
and `bool()` of a non-empty list answered a different question. The beta
deployment ran the stub while every screen was told a model was there,
which is how "unable to view the simulation" reached the owner as a
mystery instead of as a configuration line.
"""

from __future__ import annotations


def test_the_stub_reports_unavailable(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("QRME_LLM", raising=False)
    r = client.get("/studio/agent").json()
    assert r["available"] is False, (
        "the stub is answering and the door claims a model is there")


def test_a_configured_provider_reports_available(client, monkeypatch):
    from qrme import llm
    monkeypatch.setattr(llm, "default_name", lambda: "anthropic")
    assert client.get("/studio/agent").json()["available"] is True
