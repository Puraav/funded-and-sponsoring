"""findings.py turns the marts into sentences without inventing numbers."""

from fundsponsor import findings


def test_findings_come_from_the_marts(warehouse):
    document = findings.build(warehouse)
    by_id = {finding["id"]: finding for finding in document["findings"]}

    assert by_id["sponsor_rate"]["n"] == 5
    assert by_id["sponsor_rate"]["numbers"]["sponsor_rate"] == 0.8
    assert "80% of Bay Area startup raises" in by_id["sponsor_rate"]["text"]
    assert by_id["sponsor_rate"]["small_sample"]  # five raises is a small sample
    assert by_id["time_to_lca"]["numbers"]["median_days"] == 39
    # the fixture has no $50M+ raise with follow-up, so that finding is left out, not faked
    assert "by_round" not in by_id
    assert all("n" in finding for finding in document["findings"])
    assert document["match_quality"]["matched"] == 3


def test_readme_block_is_replaced_in_place(warehouse, tmp_path):
    document = findings.build(warehouse)
    readme = tmp_path / "README.md"
    readme.write_text(f"# Title\n\n{findings.START}\nold text\n{findings.END}\n\nFooter\n")

    findings.write_readme(document, readme)
    text = readme.read_text()

    assert "old text" not in text
    assert text.startswith("# Title") and text.rstrip().endswith("Footer")
    assert document["findings"][0]["text"] in text


def test_percent_format():
    assert findings.pct(0.2374) == "24%"
    assert findings.pct(0.061) == "6.1%"
    assert findings.pct(0.0999) == "10%"
