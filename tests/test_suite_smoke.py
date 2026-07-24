"""The cross-product smoke check: boots QRME + JIM-mini + PDI in-process,
seeds all three, wires the tandems, and drives one live exchange with
sealed, provable custody. Skips cleanly when the sibling packages are not
installed (the same requirement as the suite gateway)."""

import pytest

pytest.importorskip("jim", reason="jim-mini not installed alongside qrme")
pytest.importorskip("pdi", reason="pdi not installed alongside qrme")


def test_suite_smoke_is_green(tmp_path):
    from suite import smoke

    report = smoke.run(workdir=str(tmp_path))
    assert report["ok"], report
    by_name = {s["name"]: s for s in report["steps"]}
    assert by_name["end_to_end_tandem"]["detail"]["condition"] == \
        "financial_stress"
    assert "Marcus Bell" in by_name["end_to_end_tandem"]["detail"]["specialist"]
    assert by_name["custody_provenance"]["detail"]["chain_intact"] is True
