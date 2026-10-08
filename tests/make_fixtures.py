"""Build the tiny SYNTHETIC fixture files in tests/fixtures/ (real formats, invented companies).

Run `python tests/make_fixtures.py` after changing the rows below; the outputs are committed.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

SUBMISSION_COLS = (
    "ACCESSIONNUMBER FILE_NUM FILING_DATE SIC_CODE SCHEMAVERSION SUBMISSIONTYPE TESTORLIVE "
    "OVER100PERSONSFLAG OVER100ISSUERFLAG"
).split()
ISSUER_COLS = (
    "ACCESSIONNUMBER IS_PRIMARYISSUER_FLAG ISSUER_SEQ_KEY CIK ENTITYNAME STREET1 STREET2 CITY "
    "STATEORCOUNTRY STATEORCOUNTRYDESCRIPTION ZIPCODE ISSUERPHONENUMBER JURISDICTIONOFINC "
    "ISSUER_PREVIOUSNAME_1 ISSUER_PREVIOUSNAME_2 ISSUER_PREVIOUSNAME_3 EDGAR_PREVIOUSNAME_1 "
    "EDGAR_PREVIOUSNAME_2 EDGAR_PREVIOUSNAME_3 ENTITYTYPE ENTITYTYPEOTHERDESC "
    "YEAROFINC_TIMESPAN_CHOICE YEAROFINC_VALUE_ENTERED"
).split()
OFFERING_COLS = (
    "ACCESSIONNUMBER INDUSTRYGROUPTYPE INVESTMENTFUNDTYPE IS40ACT REVENUERANGE "
    "AGGREGATENETASSETVALUERANGE FEDERALEXEMPTIONS_ITEMS_LIST ISAMENDMENT PREVIOUSACCESSIONNUMBER "
    "SALE_DATE YETTOOCCUR MORETHANONEYEAR ISEQUITYTYPE ISDEBTTYPE ISOPTIONTOACQUIRETYPE "
    "ISSECURITYTOBEACQUIREDTYPE ISPOOLEDINVESTMENTFUNDTYPE ISTENANTINCOMMONTYPE "
    "ISMINERALPROPERTYTYPE ISOTHERTYPE DESCRIPTIONOFOTHERTYPE ISBUSINESSCOMBINATIONTRANS "
    "BUSCOMBCLARIFICATIONOFRESP MINIMUMINVESTMENTACCEPTED OVER100RECIPIENTFLAG "
    "TOTALOFFERINGAMOUNT TOTALAMOUNTSOLD TOTALREMAINING SALESAMTCLARIFICATIONOFRESP "
    "HASNONACCREDITEDINVESTORS NUMBERNONACCREDITEDINVESTORS TOTALNUMBERALREADYINVESTED "
    "SALESCOMM_DOLLARAMOUNT SALESCOMM_ISESTIMATE FINDERSFEE_DOLLARAMOUNT FINDERSFEE_ISESTIMATE "
    "FINDERFEECLARIFICATIONOFRESP GROSSPROCEEDSUSED_DOLLARAMOUNT GROSSPROCEEDSUSED_ISESTIMATE "
    "GROSSPROCEEDSUSED_CLAROFRESP AUTHORIZEDREPRESENTATIVE"
).split()
PERSON_COLS = (
    "ACCESSIONNUMBER RELATEDPERSON_SEQ_KEY FIRSTNAME MIDDLENAME LASTNAME STREET1 STREET2 CITY "
    "STATEORCOUNTRY STATEORCOUNTRYDESCRIPTION ZIPCODE RELATIONSHIP_1 RELATIONSHIP_2 "
    "RELATIONSHIP_3 RELATIONSHIPCLARIFICATION"
).split()

# One dict per filing. Every company is invented. Each row exists to exercise one rule.
FILINGS = [
    # 2023 Q4 (the SEC writes FILING_DATE as 05-OCT-2023 and SALE_DATE as 2023-09-28)
    dict(
        q="2023Q4",
        acc="0009000001-23-000001",
        cik="0009000001",
        name="Quillfern Robotics, Inc.",
        street="100 Fixture St",
        city="San Francisco",
        state="CA",
        zip="94107",
        filed="05-OCT-2023",
        type="D",
        industry="Other Technology",
        sale="2023-09-28",
        offered="5000000",
        sold="5000000",
        note="kept: first raise, $2-10M",
    ),
    dict(
        q="2023Q4",
        acc="0009000002-23-000001",
        cik="0009000002",
        name="Tessel Harbor Fund I, L.P.",
        street="200 Fixture St",
        city="Menlo Park",
        state="CA",
        zip="94025",
        filed="12-OCT-2023",
        type="D",
        industry="Pooled Investment Fund",
        sale="2023-10-01",
        offered="Indefinite",
        sold="12000000",
        note="dropped: fund by industry and by name",
    ),
    dict(
        q="2023Q4",
        acc="0009000003-23-000001",
        cik="0009000003",
        name="Brindlewood Software LLC",
        street="300 Fixture Ave",
        city="Austin",
        state="TX",
        zip="78701",
        filed="20-NOV-2023",
        type="D",
        industry="Other Technology",
        sale="2023-11-10",
        offered="3000000",
        sold="1500000",
        note="dropped: not in the Bay Area",
    ),
    dict(
        q="2023Q4",
        acc="0009000004-23-000001",
        cik="0009000004",
        name="Marrowgate Health Corp",
        street="400 Fixture Blvd",
        city="Palo Alto",
        state="CA",
        zip="94301-1234",
        filed="01-DEC-2023",
        type="D",
        industry="Biotechnology",
        sale="",
        offered="Indefinite",
        sold="0",
        note="kept: ZIP+4, no sale yet, nothing sold",
    ),
    # 2024 Q1
    dict(
        q="2024Q1",
        acc="0009000001-24-000002",
        cik="0009000001",
        name="Quillfern Robotics, Inc.",
        street="100 Fixture St",
        city="San Francisco",
        state="CA",
        zip="94107",
        filed="15-JAN-2024",
        type="D/A",
        industry="Other Technology",
        sale="2023-09-28",
        offered="5000000",
        sold="5000000",
        note="dropped: amendment",
    ),
    dict(
        q="2024Q1",
        acc="0009000001-24-000003",
        cik="0009000001",
        name="Quillfern Robotics, Inc.",
        street="100 Fixture St",
        city="San Francisco",
        state="CA",
        zip="94107",
        filed="20-MAR-2024",
        type="D",
        industry="Other Technology",
        sale="2024-03-01",
        offered="30000000",
        sold="25000000",
        note="kept: second raise, $10-50M",
    ),
    dict(
        q="2024Q1",
        acc="0009000005-24-000001",
        cik="0009000005",
        name="Oakmere Capital Partners",
        street="500 Fixture Way",
        city="Oakland",
        state="CA",
        zip="94612",
        filed="02-FEB-2024",
        type="D",
        industry="Other",
        sale="2024-01-20",
        offered="8000000",
        sold="8000000",
        note="dropped: fund by name only",
    ),
    dict(
        q="2024Q1",
        acc="0009000006-24-000001",
        cik="0009000006",
        name="Sablewick Properties Inc",
        street="600 Fixture Rd",
        city="San Jose",
        state="CA",
        zip="95113",
        filed="09-FEB-2024",
        type="D",
        industry="Commercial",
        sale="2024-02-01",
        offered="60000000",
        sold="60000000",
        note="dropped: real estate industry",
    ),
    dict(
        q="2024Q1",
        acc="0009000007-24-000001",
        cik="0009000007",
        name="Nimbus Thistle AI, Inc.",
        street="700 Fixture Ln",
        city="Berkeley",
        state="CA",
        zip="94704",
        filed="28-FEB-2024",
        type="D",
        industry="Other Technology",
        sale="2024-02-15",
        offered="900000",
        sold="750000",
        note="kept: first raise, under $2M",
    ),
]


def _tsv(columns: list[str], rows: list[dict]) -> str:
    lines = ["\t".join(columns)]
    lines += ["\t".join(str(row.get(col, "")) for col in columns) for row in rows]
    return "\n".join(lines) + "\n"


def formd_tables(quarter: str) -> dict[str, str]:
    """The four Form D tables for one quarter, as tab-delimited text."""
    filings = [f for f in FILINGS if f["q"] == quarter]
    submissions = [
        dict(
            ACCESSIONNUMBER=f["acc"],
            FILE_NUM="021-000000",
            FILING_DATE=f["filed"],
            SCHEMAVERSION="X0708",
            SUBMISSIONTYPE=f["type"],
            TESTORLIVE="LIVE",
        )
        for f in filings
    ]
    issuers = [
        dict(
            ACCESSIONNUMBER=f["acc"],
            IS_PRIMARYISSUER_FLAG="YES",
            ISSUER_SEQ_KEY="101",
            CIK=f["cik"],
            ENTITYNAME=f["name"],
            STREET1=f["street"],
            CITY=f["city"],
            STATEORCOUNTRY=f["state"],
            ZIPCODE=f["zip"],
            ENTITYTYPE="Corporation",
        )
        for f in filings
    ]
    # A second, non-primary issuer on the first filing: must never create a duplicate raise.
    issuers += [
        dict(
            ACCESSIONNUMBER=f["acc"],
            IS_PRIMARYISSUER_FLAG="NO",
            ISSUER_SEQ_KEY="102",
            CIK="0009000099",
            ENTITYNAME="Quillfern Robotics Holdings",
            STREET1=f["street"],
            CITY=f["city"],
            STATEORCOUNTRY=f["state"],
            ZIPCODE=f["zip"],
        )
        for f in filings[:1]
        if quarter == "2023Q4"
    ]
    offerings = [
        dict(
            ACCESSIONNUMBER=f["acc"],
            INDUSTRYGROUPTYPE=f["industry"],
            ISAMENDMENT="true" if f["type"] == "D/A" else "false",
            SALE_DATE=f["sale"],
            ISEQUITYTYPE="true",
            TOTALOFFERINGAMOUNT=f["offered"],
            TOTALAMOUNTSOLD=f["sold"],
        )
        for f in filings
    ]
    people = [
        dict(
            ACCESSIONNUMBER=f["acc"],
            RELATEDPERSON_SEQ_KEY="103",
            FIRSTNAME="Fixture",
            LASTNAME=f"Person{i}",
            CITY=f["city"],
            STATEORCOUNTRY=f["state"],
            ZIPCODE=f["zip"],
            RELATIONSHIP_1="Executive Officer",
            RELATIONSHIP_2="Director",
        )
        for i, f in enumerate(filings)
    ]
    return {
        "FORMDSUBMISSION": _tsv(SUBMISSION_COLS, submissions),
        "ISSUERS": _tsv(ISSUER_COLS, issuers),
        "OFFERING": _tsv(OFFERING_COLS, offerings),
        "RELATEDPERSONS": _tsv(PERSON_COLS, people),
    }


def write_formd_zips(dest: Path) -> list[Path]:
    """Write one ZIP per quarter with the SEC's layout: {YYYY}Q{Q}_d/{TABLE}.tsv."""
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for quarter in sorted({f["q"] for f in FILINGS}):
        path = dest / f"{quarter.lower()}_d.zip"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for table, text in formd_tables(quarter).items():
                info = zipfile.ZipInfo(f"{quarter}_d/{table}.tsv", date_time=(2024, 1, 1, 0, 0, 0))
                archive.writestr(info, text)
        paths.append(path)
    return paths


def main() -> None:
    for path in write_formd_zips(FIXTURES / "formd_zips"):
        print(f"wrote {path.relative_to(FIXTURES.parent.parent)}")


if __name__ == "__main__":
    main()
