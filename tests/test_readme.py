"""Every number in the README comes from data/findings.json, not from typing."""

import json
from pathlib import Path

from fundsponsor import findings

ROOT = Path(__file__).resolve().parents[1]


def between(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def test_readme_blocks_match_findings_json():
    document = json.loads((ROOT / "data" / "findings.json").read_text())
    readme = (ROOT / "README.md").read_text()

    assert between(readme, findings.START, findings.END) == findings.readme_block(document)
    assert between(readme, findings.STATS_START, findings.STATS_END) == findings.stats_block(
        document
    )


def test_site_findings_match_too():
    document = json.loads((ROOT / "data" / "findings.json").read_text())
    site = json.loads((ROOT / "web" / "public" / "data" / "findings.json").read_text())
    assert site["findings"] == document["findings"]
    assert site["match_quality"] == document["match_quality"]


def test_readme_never_says_hired():
    # an LCA is a filing, not a hire: the project's wording rule
    text = (ROOT / "README.md").read_text().lower()
    assert "hired h-1b" not in text
