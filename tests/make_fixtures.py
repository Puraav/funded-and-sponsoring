"""Build the tiny SYNTHETIC fixture files in tests/fixtures/ (real formats, invented companies).

Run `python tests/make_fixtures.py` after changing the rows below; the outputs are committed.
"""

from __future__ import annotations

import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import openpyxl

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
    # 2023 Q3: before the 2023-10-01 cut-off, but it still makes the 2024 raise "not first"
    dict(
        q="2023Q3",
        acc="0009000007-23-000001",
        cik="0009000007",
        name="Nimbus Thistle AI, Inc.",
        street="700 Fixture Ln",
        city="Berkeley",
        state="CA",
        zip="94704",
        filed="15-SEP-2023",
        type="D",
        industry="Other Technology",
        sale="2023-09-01",
        offered="500000",
        sold="500000",
        note="dropped: filed before 2023-10-01",
    ),
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
        note="kept: second raise on record, under $2M",
    ),
    dict(
        q="2024Q1",
        acc="0009000008-24-000001",
        cik="0009000008",
        name="Gantry Row 12 LLC",
        street="800 Fixture Ct",
        city="Oakland",
        state="CA",
        zip="94612",
        filed="05-MAR-2024",
        type="D",
        industry="Other",
        sale="2024-03-01",
        offered="4000000",
        sold="4000000",
        entity="Limited Liability Company",
        note="dropped: LLC under the catch-all Other industry",
    ),
    dict(
        q="2024Q1",
        acc="0009000009-24-000001",
        cik="0009000009",
        name="Harrowfield Systems, Inc.",
        street="900 Fixture Dr",
        city="Sunnyvale",
        state="CA",
        zip="94085",
        filed="12-MAR-2024",
        type="D",
        industry="Other Technology",
        sale="2024-03-05",
        offered="70000000",
        sold="70000000",
        merger="true",
        note="dropped: business combination",
    ),
    dict(
        q="2024Q1",
        acc="0009000010-24-000001",
        cik="0009000010",
        name="Nova, Inc.",
        street="1000 Fixture Pl",
        city="San Francisco",
        state="CA",
        zip="94107",
        filed="10-JAN-2024",
        type="D",
        industry="Other Technology",
        sale="2024-01-02",
        offered="3000000",
        sold="3000000",
        note="kept: generic name, so it may only match an employer in the same ZIP",
    ),
    dict(
        q="2024Q1",
        acc="0009000011-24-000001",
        cik="0009000011",
        name="Corvane Semiconductor Corp",
        street="1100 Fixture Pkwy",
        city="Santa Clara",
        state="CA",
        zip="95054",
        filed="14-FEB-2024",
        type="D",
        industry="Other Technology",
        sale="2024-02-10",
        offered="40000000",
        sold="40000000",
        sic="3674",
        note="dropped: has an SEC industry code, so it is a listed company",
    ),
    # 2025 Q1: too recent to have a full year of LCA data after it
    dict(
        q="2025Q1",
        acc="0009000004-25-000002",
        cik="0009000004",
        name="Marrowgate Health Corp",
        street="400 Fixture Blvd",
        city="Palo Alto",
        state="CA",
        zip="94301",
        filed="15-JAN-2025",
        type="D",
        industry="Biotechnology",
        sale="2025-01-10",
        offered="60000000",
        sold="60000000",
        note="kept, but without full follow-up it is left out of every rate",
    ),
]


# The real 96-column header of the DOL LCA disclosure files (FY2023 onward).
LCA_COLS = (
    "CASE_NUMBER CASE_STATUS RECEIVED_DATE DECISION_DATE ORIGINAL_CERT_DATE VISA_CLASS JOB_TITLE "
    "SOC_CODE SOC_TITLE FULL_TIME_POSITION BEGIN_DATE END_DATE TOTAL_WORKER_POSITIONS "
    "NEW_EMPLOYMENT CONTINUED_EMPLOYMENT CHANGE_PREVIOUS_EMPLOYMENT NEW_CONCURRENT_EMPLOYMENT "
    "CHANGE_EMPLOYER AMENDED_PETITION EMPLOYER_NAME TRADE_NAME_DBA EMPLOYER_ADDRESS1 "
    "EMPLOYER_ADDRESS2 EMPLOYER_CITY EMPLOYER_STATE EMPLOYER_POSTAL_CODE EMPLOYER_COUNTRY "
    "EMPLOYER_PROVINCE EMPLOYER_PHONE EMPLOYER_PHONE_EXT NAICS_CODE EMPLOYER_POC_LAST_NAME "
    "EMPLOYER_POC_FIRST_NAME EMPLOYER_POC_MIDDLE_NAME EMPLOYER_POC_JOB_TITLE "
    "EMPLOYER_POC_ADDRESS1 EMPLOYER_POC_ADDRESS2 EMPLOYER_POC_CITY EMPLOYER_POC_STATE "
    "EMPLOYER_POC_POSTAL_CODE EMPLOYER_POC_COUNTRY EMPLOYER_POC_PROVINCE EMPLOYER_POC_PHONE "
    "EMPLOYER_POC_PHONE_EXT EMPLOYER_POC_EMAIL AGENT_REPRESENTING_EMPLOYER "
    "AGENT_ATTORNEY_LAST_NAME AGENT_ATTORNEY_FIRST_NAME AGENT_ATTORNEY_MIDDLE_NAME "
    "AGENT_ATTORNEY_ADDRESS1 AGENT_ATTORNEY_ADDRESS2 AGENT_ATTORNEY_CITY AGENT_ATTORNEY_STATE "
    "AGENT_ATTORNEY_POSTAL_CODE AGENT_ATTORNEY_COUNTRY AGENT_ATTORNEY_PROVINCE "
    "AGENT_ATTORNEY_PHONE AGENT_ATTORNEY_PHONE_EXT AGENT_ATTORNEY_EMAIL_ADDRESS "
    "LAWFIRM_NAME_BUSINESS_NAME STATE_OF_HIGHEST_COURT NAME_OF_HIGHEST_STATE_COURT "
    "WORKSITE_WORKERS SECONDARY_ENTITY SECONDARY_ENTITY_BUSINESS_NAME WORKSITE_ADDRESS1 "
    "WORKSITE_ADDRESS2 WORKSITE_CITY WORKSITE_COUNTY WORKSITE_STATE WORKSITE_POSTAL_CODE "
    "WAGE_RATE_OF_PAY_FROM WAGE_RATE_OF_PAY_TO WAGE_UNIT_OF_PAY PREVAILING_WAGE PW_UNIT_OF_PAY "
    "PW_TRACKING_NUMBER PW_WAGE_LEVEL PW_OES_YEAR PW_OTHER_SOURCE PW_OTHER_YEAR "
    "PW_SURVEY_PUBLISHER PW_SURVEY_NAME TOTAL_WORKSITE_LOCATIONS AGREE_TO_LC_STATEMENT "
    "H_1B_DEPENDENT WILLFUL_VIOLATOR SUPPORT_H1B STATUTORY_BASIS APPENDIX_A_ATTACHED "
    "PUBLIC_DISCLOSURE PREPARER_LAST_NAME PREPARER_FIRST_NAME PREPARER_MIDDLE_INITIAL "
    "PREPARER_BUSINESS_NAME PREPARER_EMAIL"
).split()

EMPLOYERS = {
    # key: (EMPLOYER_NAME, TRADE_NAME_DBA, address, city, state, zip, naics)
    "quillfern": (
        "QUILLFERN ROBOTICS INC",
        "",
        "100 Fixture St",
        "San Francisco",
        "CA",
        "94107",
        "541715",
    ),
    "nimbus": (
        "Nimbus Thistle AI, Inc.",
        "Thistle",
        "700 Fixture Ln",
        "Berkeley",
        "CA",
        "94704",
        "541511",
    ),
    "marrowgate": (
        "Marrowgate Health Corporation",
        "",
        "400 Fixture Blvd",
        "Palo Alto",
        "CA",
        "94301",
        "541714",
    ),
    "bigco": ("Ferrowmont Systems LLC", "", "1 Fixture Plaza", "Seattle", "WA", "98101", "541512"),
    "brindle": (
        "Brindlewood Software LLC",
        "",
        "300 Fixture Ave",
        "Austin",
        "TX",
        "78701",
        "541511",
    ),
    # Other records of the fixture startups, one per matching rule
    "quillfern_oak": (
        "Quillfern Robotics Inc.",
        "",
        "5 Dock Rd",
        "Oakland",
        "CA",
        "94612",
        "541715",
    ),  # rule 2: same name, another Bay Area ZIP
    "marrowgate_la": (
        "Marrowgate Health",
        "",
        "9 Sunset Blvd",
        "Los Angeles",
        "CA",
        "90012",
        "541714",
    ),  # rule 3: same name, elsewhere in California
    "quillfern_typo": (
        "Quillfern Robotic Inc",
        "",
        "7 Fixture St",
        "San Francisco",
        "CA",
        "94105",
        "541715",
    ),  # rule 4: one letter off, same 3-digit ZIP
    "nova_la": ("Nova Inc", "", "1 Venice Way", "Los Angeles", "CA", "90291", "541511"),
    # A Bay Area office of the big employer: a Bay Area sponsor that is not a startup
    "bigco_sf": (
        "Ferrowmont Systems LLC",
        "",
        "2 Fixture Plaza",
        "San Francisco",
        "CA",
        "94105",
        "541512",
    ),
}


def _lca(
    case,
    employer,
    received,
    title,
    soc,
    soc_title,
    wage,
    unit="Year",
    level="II",
    status="Certified",
    visa="H-1B",
    new=1,
    cont=0,
    change=0,
    pw=None,
    decided=None,
):
    """One LCA row. Dates are YYYY-MM-DD; `decided` defaults to a week after `received`."""
    name, dba, address, city, state, zip_code, naics = EMPLOYERS[employer]
    got = datetime.strptime(received, "%Y-%m-%d")
    done = datetime.strptime(decided, "%Y-%m-%d") if decided else got + timedelta(days=7)
    return dict(
        CASE_NUMBER=case,
        CASE_STATUS=status,
        RECEIVED_DATE=got,
        DECISION_DATE=done,
        VISA_CLASS=visa,
        JOB_TITLE=f'="{title}"',
        SOC_CODE=f'="{soc}"',
        SOC_TITLE=soc_title,
        FULL_TIME_POSITION="Y",
        BEGIN_DATE=got + timedelta(days=30),
        TOTAL_WORKER_POSITIONS=1,
        NEW_EMPLOYMENT=new,
        CONTINUED_EMPLOYMENT=cont,
        CHANGE_EMPLOYER=change,
        EMPLOYER_NAME=name,
        TRADE_NAME_DBA=f'="{dba}"',
        EMPLOYER_ADDRESS1=address,
        EMPLOYER_CITY=city,
        EMPLOYER_STATE=state,
        EMPLOYER_POSTAL_CODE=f'="{zip_code}"',
        EMPLOYER_COUNTRY="UNITED STATES OF AMERICA",
        NAICS_CODE=f'="{naics}"',
        WORKSITE_CITY=city,
        WORKSITE_STATE=state,
        WORKSITE_POSTAL_CODE=f'="{zip_code}"',
        WAGE_RATE_OF_PAY_FROM=wage,
        WAGE_UNIT_OF_PAY=unit,
        PREVAILING_WAGE=pw if pw is not None else wage * 0.9,
        PW_UNIT_OF_PAY=unit,
        PW_WAGE_LEVEL=level,
    )


# Every row is invented. 20 rows in the first file, 7 in the second (one case repeats).
LCA_FILES = {
    ("LCA_Disclosure_Data_FY2024_Q2.xlsx", 2024, 2): [
        # Quillfern: sponsored BEFORE its first raise (Oct 2023) and after it
        _lca(
            "I-200-23001-000001",
            "quillfern",
            "2023-01-10",
            "Robotics Software Engineer",
            "15-1252.00",
            "Software Developers",
            165000,
            level="II",
        ),
        _lca(
            "I-200-23300-000002",
            "quillfern",
            "2023-11-02",
            "Software Engineer I",
            "15-1252.00",
            "Software Developers",
            138000,
            level="I",
        ),
        _lca(
            "I-200-23310-000003",
            "quillfern",
            "2023-11-14",
            "Data Scientist",
            "15-2051.00",
            "Data Scientists",
            172000,
            level="III",
        ),
        _lca(
            "I-200-24010-000004",
            "quillfern",
            "2024-01-12",
            "Senior Product Manager",
            "11-2021.00",
            "Marketing Managers",
            205000,
            level="IV",
            new=0,
            change=1,
        ),
        _lca(
            "I-200-24020-000005",
            "quillfern",
            "2024-01-20",
            "Mechanical Engineer",
            "17-2141.00",
            "Mechanical Engineers",
            150000,
            level="II",
            new=0,
            cont=1,
        ),
        _lca(
            "I-200-24030-000006",
            "quillfern",
            "2024-02-01",
            "Software Engineer",
            "15-1252.00",
            "Software Developers",
            82.5,
            unit="Hour",
            level="II",
        ),
        _lca(
            "I-200-24040-000007",
            "quillfern",
            "2024-02-10",
            "Software Engineer",
            "15-1252.00",
            "Software Developers",
            150000,
            status="Withdrawn",
        ),
        _lca(
            "I-203-24041-000008",
            "quillfern",
            "2024-02-11",
            "Software Engineer",
            "15-1252.00",
            "Software Developers",
            150000,
            visa="E-3 Australian",
        ),
        # Nimbus Thistle AI: first raise Feb 2024, first LCA 20 days later
        _lca(
            "I-200-24079-000009",
            "nimbus",
            "2024-03-19",
            "Machine Learning Engineer",
            "15-1252.00",
            "Software Developers",
            190000,
            level="II",
        ),
        _lca(
            "I-200-24080-000010",
            "nimbus",
            "2024-03-20",
            "Member of Technical Staff",
            "15-1299.08",
            "Computer Systems Engineers/Architects",
            14000,
            unit="Month",
            level="I",
        ),
        # Marrowgate: name differs only by legal suffix (Corp / Corporation)
        _lca(
            "I-200-24050-000011",
            "marrowgate",
            "2024-02-19",
            "Research Scientist",
            "19-1042.00",
            "Medical Scientists",
            128000,
            level="II",
        ),
        _lca(
            "I-200-24051-000012",
            "marrowgate",
            "2024-02-20",
            "Bioinformatics Data Analyst",
            "15-2041.00",
            "Statisticians",
            3100,
            unit="Bi-Weekly",
            level="I",
        ),
        # A big non-startup employer, never in Form D
        _lca(
            "I-200-24001-000013",
            "bigco",
            "2024-01-03",
            "Systems Analyst",
            "15-1211.00",
            "Computer Systems Analysts",
            98000,
            level="I",
        ),
        _lca(
            "I-200-24002-000014",
            "bigco",
            "2024-01-04",
            "Systems Analyst",
            "15-1211.00",
            "Computer Systems Analysts",
            99000,
            level="I",
        ),
        _lca(
            "I-200-24003-000015",
            "bigco",
            "2024-01-05",
            "Software Developer",
            "15-1252.00",
            "Software Developers",
            121000,
            level="II",
        ),
        _lca(
            "I-200-24004-000016",
            "bigco",
            "2024-01-08",
            "Accountant",
            "13-2011.00",
            "Accountants and Auditors",
            1650,
            unit="Week",
            level="II",
        ),
        _lca(
            "I-201-24005-000017",
            "bigco",
            "2024-01-09",
            "Software Developer",
            "15-1252.00",
            "Software Developers",
            118000,
            visa="H-1B1 Chile",
        ),
        _lca(
            "I-200-24006-000018",
            "bigco",
            "2024-01-10",
            "Software Developer",
            "15-1252.00",
            "Software Developers",
            5000000,
            level="II",
        ),  # absurd wage → null
        # Brindlewood: a Texas startup that raised but is outside the Bay Area
        _lca(
            "I-200-24060-000019",
            "brindle",
            "2024-03-01",
            "Software Engineer",
            "15-1252.00",
            "Software Developers",
            132000,
            level="II",
        ),
        # A certified case that is later withdrawn in the next quarter's file
        _lca(
            "I-200-24085-000020",
            "nimbus",
            "2024-03-25",
            "Software Engineer",
            "15-1252.00",
            "Software Developers",
            176000,
            level="II",
        ),
    ],
    ("LCA_Disclosure_Data_FY2024_Q3.xlsx", 2024, 3): [
        _lca(
            "I-200-24085-000020",
            "nimbus",
            "2024-03-25",
            "Software Engineer",
            "15-1252.00",
            "Software Developers",
            176000,
            level="II",
            status="Certified - Withdrawn",
            decided="2024-04-20",
        ),
        _lca(
            "I-200-24100-000021",
            "nimbus",
            "2024-04-09",
            "Product Manager",
            "15-1299.09",
            "Information Technology Project Managers",
            168000,
            level="II",
        ),
        _lca(
            "I-200-24130-000022",
            "quillfern",
            "2024-05-09",
            "Data Engineer",
            "15-1243.00",
            "Database Architects",
            158000,
            level="II",
        ),
        _lca(
            "I-200-24140-000023",
            "quillfern_oak",
            "2024-05-20",
            "Firmware Engineer",
            "17-2061.00",
            "Computer Hardware Engineers",
            149000,
            level="II",
        ),
        _lca(
            "I-200-24141-000024",
            "marrowgate_la",
            "2024-05-21",
            "Lab Operations Manager",
            "11-9121.00",
            "Natural Sciences Managers",
            140000,
            level="III",
        ),
        _lca(
            "I-200-24142-000025",
            "quillfern_typo",
            "2024-05-22",
            "Controls Engineer",
            "17-2071.00",
            "Electrical Engineers",
            145000,
            level="II",
        ),
        # A different company that happens to be called Nova: must not match the startup
        _lca(
            "I-200-24143-000026",
            "nova_la",
            "2024-05-23",
            "Software Engineer",
            "15-1252.00",
            "Software Developers",
            130000,
            level="II",
        ),
    ],
    # The latest LCA sets how far the data reaches: raises up to a year before it can be judged
    ("LCA_Disclosure_Data_FY2025_Q3.xlsx", 2025, 3): [
        _lca(
            "I-200-25100-000027",
            "bigco_sf",
            "2025-04-10",
            "Systems Analyst",
            "15-1211.00",
            "Computer Systems Analysts",
            104000,
            level="II",
        ),
    ],
}


def write_lca_xlsx(dest: Path) -> list[tuple[Path, int, int]]:
    """Write the synthetic LCA Excel files. Returns (path, fiscal_year, quarter)."""
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for (name, fiscal_year, quarter), rows in LCA_FILES.items():
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = name.removesuffix(".xlsx")[:31]
        sheet.append(LCA_COLS)
        for row in rows:
            sheet.append([row.get(col) for col in LCA_COLS])
        # Fixed timestamps keep the committed file byte-stable between runs.
        workbook.properties.created = workbook.properties.modified = datetime(2024, 1, 1)
        workbook.save(dest / name)
        written.append((dest / name, fiscal_year, quarter))
    return written


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
            SIC_CODE=f.get("sic", ""),
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
            ENTITYTYPE=f.get("entity", "Corporation"),
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
            ISBUSINESSCOMBINATIONTRANS=f.get("merger", "false"),
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
    from fundsponsor import fetch_formd, fetch_lca

    zips = write_formd_zips(FIXTURES / "formd_zips")
    files = write_lca_xlsx(FIXTURES / "lca_xlsx")
    for path in [*zips, *(f[0] for f in files)]:
        print(f"wrote {path.relative_to(FIXTURES.parent.parent)}")

    # The same raw layout as data/raw/, so dbt can build on it (FS_DATA_DIR=tests/fixtures/raw).
    raw = FIXTURES / "raw"
    fetch_formd.run(raw / "formd", zips)
    with tempfile.TemporaryDirectory() as scratch:
        jobs = [(x, Path(scratch) / f"{x.stem}.parquet", fy, q) for x, fy, q in files]
        fetch_lca.run(jobs, raw / "lca" / "lca_all.parquet")
    print(f"wrote {raw.relative_to(FIXTURES.parent.parent)}/")


if __name__ == "__main__":
    main()
