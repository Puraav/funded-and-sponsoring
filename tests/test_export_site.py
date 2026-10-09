"""export_site writes the JSON files the website reads."""

import json

from fundsponsor import export_site


def test_export_writes_every_file_the_site_needs(warehouse, tmp_path):
    export_site.export(warehouse, tmp_path)

    for name in ("findings", "metrics", "match_quality", "companies", "radar"):
        assert (tmp_path / f"{name}.json").exists(), name

    companies = json.loads((tmp_path / "companies.json").read_text())
    by_slug = {company["slug"]: company for company in companies}
    assert set(by_slug) == {
        "marrowgate-health-corp", "nimbus-thistle-ai-inc", "nova-inc", "quillfern-robotics-inc",
    }  # fmt: skip
    assert not by_slug["nova-inc"]["has_page"]  # no matched H-1B filing, so no page

    # a page only for companies with at least one matched filing
    pages = sorted(path.stem for path in (tmp_path / "company").glob("*.json"))
    assert pages == ["marrowgate-health-corp", "nimbus-thistle-ai-inc", "quillfern-robotics-inc"]

    quillfern = json.loads((tmp_path / "company" / "quillfern-robotics-inc.json").read_text())
    assert quillfern["lcas_total"] == 9
    assert [r["filing_date"] for r in quillfern["raise_list"]] == ["2023-10-05", "2024-03-20"]
    assert sum(m["lcas"] for m in quillfern["monthly_lcas"]) == 9
    assert quillfern["officers"][0]["relationships"] == "Executive Officer, Director"
    # officers carry a name and a role only, never an address
    assert set(quillfern["officers"][0]) == {"name", "relationships"}

    metrics = json.loads((tmp_path / "metrics.json").read_text())
    assert [row["round_bin"] for row in metrics["mart_by_round"]][0] == "<$2M"


def test_clean_makes_values_json_safe():
    import datetime
    import decimal

    assert export_site.clean(datetime.date(2024, 3, 1)) == "2024-03-01"
    assert export_site.clean(decimal.Decimal("5.00")) == 5
    assert export_site.clean(float("nan")) is None
    assert export_site.clean(0.123456) == 0.1235
