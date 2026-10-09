"""The radar: parsing EDGAR Form D XML, scoring in dbt, and the exported list."""

import datetime
import json
from pathlib import Path

from fundsponsor import export_radar, fetch_edgar_recent

EDGAR = Path(__file__).parent / "fixtures" / "edgar"


def test_parse_form_d_xml():
    xml = (EDGAR / "0009000001-24-000009.xml").read_bytes()
    record = fetch_edgar_recent.parse_form_d(
        xml, "0009000001-24-000009", datetime.date(2024, 6, 10)
    )
    assert record["cik"] == "0009000001"
    assert record["entity_name"] == "Quillfern Robotics, Inc."
    assert (record["city"], record["state"], record["zipcode"]) == ("San Francisco", "CA", "94107")
    assert record["industry_group"] == "Other Technology"
    assert record["amount_sold"] == 12_000_000
    assert record["first_sale_date"] == datetime.date(2024, 6, 1)
    assert record["is_business_combination"] is False
    # only the executive officer is kept, by name; the director and all addresses are not
    assert record["officers"] == "Fixture Founder"


def test_parse_form_d_indefinite_amount():
    xml = (EDGAR / "0009000012-24-000001.xml").read_bytes()
    record = fetch_edgar_recent.parse_form_d(xml, "x", datetime.date(2024, 6, 11))
    assert record["amount_offered"] is None
    assert record["entity_type"] == "Limited Partnership"


def test_index_rows_keep_only_original_form_d():
    index = "\n".join(
        [
            "Form Type   Company Name      CIK     Date Filed  File Name",
            "-----------------------------------------------------------",
            "D     Quillfern Robotics, Inc.   9000001  20240610  edgar/data/9000001/0009000001-24-000009.txt",
            "D/A   Quillfern Robotics, Inc.   9000001  20240610  edgar/data/9000001/0009000001-24-000010.txt",
            "10-K  D Something Corp           1234     20240610  edgar/data/1234/0000001234-24-000001.txt",
        ]
    )
    assert fetch_edgar_recent.index_rows(index) == [
        {
            "cik": "9000001",
            "accession": "0009000001-24-000009",
            "filing_date": datetime.date(2024, 6, 10),
        }
    ]


def test_business_days_skip_weekends():
    days = fetch_edgar_recent.business_days(6, datetime.date(2024, 6, 10))  # a Monday
    assert [d.isoformat() for d in days] == [
        "2024-06-04", "2024-06-05", "2024-06-06", "2024-06-07", "2024-06-10",
    ]  # fmt: skip


def test_radar_scores(warehouse):
    rows = warehouse.sql(
        """select rank, company, score, lcas_24m, software_lcas, data_lcas, product_lcas,
                  early_career_lcas, reasons
           from radar order by rank"""
    ).fetchall()
    # the fund is filtered out by the same rules as the quarterly raises
    assert [row[1] for row in rows] == ["Quillfern Robotics, Inc.", "Hollowbrook Labs, Inc."]

    # Quillfern: 8 filings in 24 months → 40 * ln(9) / ln(51) = 22.4, plus 25 (tech roles),
    # 15 (early-career) and 15 ($10-50M raise) = 77
    assert rows[0][2:8] == (77, 8, 3, 2, 1, 6)
    assert rows[0][8] == (
        "8 H-1B filings since Jan 2023, 3 for software roles, 2 for data roles, "
        "1 for product roles, 6 early-career."
    )
    # Hollowbrook: no history, 5 points for a raise under $2M
    assert rows[1][2:4] == (5, 0)
    assert rows[1][8] == "No H-1B filings found in the last 24 months."


def test_radar_matching_has_no_fuzzy_rule(warehouse):
    employers = warehouse.sql(
        "select employer_name, match_rule from int_recent_matches order by match_rule"
    ).fetchall()
    assert employers == [("QUILLFERN ROBOTICS INC", 1), ("Quillfern Robotics Inc.", 2)]


def test_export_radar_writes_json_and_markdown(warehouse, tmp_path):
    web = tmp_path / "web"
    web.mkdir()
    (web / "companies.json").write_text(
        json.dumps([{"cik": "0009000001", "slug": "quillfern-robotics-inc", "has_page": True}])
    )
    radar = export_radar.export(warehouse, web, tmp_path / "radar", datetime.date(2024, 6, 17))

    assert radar["generated"] == "2024-06-17"
    assert radar["startups_considered"] == 2
    assert radar["rows"][0]["slug"] == "quillfern-robotics-inc"
    assert radar["rows"][1]["slug"] is None
    assert radar["rows"][0]["sec_url"].endswith("/9000001/000900000124000009/")
    assert json.loads((web / "radar.json").read_text())["rows"][0]["score"] == 77

    text = (tmp_path / "radar" / "radar_2024-06-17.md").read_text()
    assert "| 1 | Quillfern Robotics, Inc. | San Francisco | $12.0M | 77 |" in text
