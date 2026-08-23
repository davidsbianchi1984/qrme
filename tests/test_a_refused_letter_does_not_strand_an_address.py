"""A refused letter does not strand an address.

`accounts.signup` writes the account row and commits it, and only then sends
the verification code. Until a mail server existed that send could not fail —
with none configured `mailer.deliver` prints on the server and returns — so
it was never wrapped.

    asked     did the code go
    mattered  can this person ever sign up

An unhandled refusal there costs more than the letter. The caller gets a 500,
the pending account survives the request that failed, and the next attempt
from the same address is turned away as *already pending* — naming a code
nobody ever received. One transient outage at the mail host, and that address
cannot create an account.

JIM-mini carries the identical shape and the identical fix; this is the same
sentence in the other product, which is the only reason it is here twice.
"""

import smtplib

import pytest

from qrme import accounts, mailer


@pytest.fixture
def refusing_server(monkeypatch):
    def refuse(*a, **k):
        raise smtplib.SMTPServerDisconnected("connection lost")
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    monkeypatch.setattr(mailer, "deliver", refuse)


def test_signup_answers_instead_of_raising(client, refusing_server):
    """The person gets an answer, and it says the code did not go."""
    out = accounts.signup("stranded@example.com", "a-long-enough-password",
                          display_name="Sam")
    assert out["code_delivery"] == "failed"


def test_the_way_back_stays_open(client, refusing_server):
    """`resend` is the recovery path, so it must answer too rather than
    raising — a 500 there would close the only door out."""
    accounts.signup("stranded@example.com", "a-long-enough-password",
                    display_name="Sam")
    again = accounts.resend("stranded@example.com")
    assert again["code_delivery"] == "failed"


def test_a_reset_that_cannot_be_mailed_says_so(client, refusing_server):
    """The other sentence `_send_code` carries. Same treatment, because a
    reset that 500s tells somebody locked out of an account nothing at all."""
    accounts.signup("sam@example.com", "a-long-enough-password",
                    display_name="Sam")
    out = accounts.request_reset("sam@example.com")
    assert out["code_delivery"] in ("failed", "none")
