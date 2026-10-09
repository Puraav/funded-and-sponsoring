"""Build the dbt project on the synthetic fixtures and check the rules that matter."""


def test_only_bay_area_startup_raises_are_kept(warehouse):
    rows = warehouse.sql(
        "select accession, round_bin, is_first_raise from int_bay_area_raises order by accession"
    ).fetchall()
    # Dropped: amendment, fund (industry and name), Texas company, real estate, LLC under
    # "Other", business combination, listed company, and the filing before 2023-10-01.
    assert rows == [
        ("0009000001-23-000001", "$2–10M", True),  # Quillfern, first raise
        ("0009000001-24-000003", "$10–50M", False),  # Quillfern, second raise
        ("0009000004-23-000001", "unknown", True),  # Marrowgate, nothing sold yet
        ("0009000004-25-000002", "$50M+", False),  # Marrowgate, second raise
        ("0009000007-24-000001", "<$2M", False),  # Nimbus, raised before the cut-off too
        ("0009000010-24-000001", "$2–10M", True),  # Nova
    ]


def test_dim_company_is_one_row_per_company(warehouse):
    rows = warehouse.sql(
        "select company_slug, county_name, raise_count, total_sold from dim_company order by 1"
    ).fetchall()
    assert rows == [
        ("marrowgate-health-corp", "Santa Clara", 2, 60_000_000),
        ("nimbus-thistle-ai-inc", "Alameda", 1, 750_000),
        ("nova-inc", "San Francisco", 1, 3_000_000),
        ("quillfern-robotics-inc", "San Francisco", 2, 30_000_000),
    ]


def test_only_certified_h1b_cases_are_events(warehouse):
    cases = {row[0] for row in warehouse.sql("select case_number from int_lca_h1b").fetchall()}
    assert len(cases) == 23
    # Withdrawn, E-3, H-1B1 and certified-then-withdrawn cases are not sponsoring events.
    assert not cases & {
        "I-200-24040-000007",
        "I-203-24041-000008",
        "I-201-24005-000017",
        "I-200-24085-000020",
    }


def test_role_groups_wages_and_new_hire_flag(warehouse):
    rows = {
        case: (role, wage, new_hire)
        for case, role, wage, new_hire in warehouse.sql(
            "select case_number, role_group, annual_wage, is_new_hire from int_lca_h1b"
        ).fetchall()
    }
    assert rows["I-200-23001-000001"] == ("Software", 165_000, True)
    # change of employer counts as a new hire; the title beats the marketing-manager SOC code
    assert rows["I-200-24010-000004"] == ("Product", 205_000, True)
    assert rows["I-200-24020-000005"] == ("Non-tech", 150_000, False)  # an extension
    assert rows["I-200-24030-000006"] == ("Software", 171_600, True)  # $82.50 an hour
    assert rows["I-200-24079-000009"][0] == "Data"  # "Machine Learning" beats a software SOC
    assert rows["I-200-24080-000010"] == ("Other tech", 168_000, True)  # $14,000 a month
    assert rows["I-200-24051-000012"] == ("Data", 80_600, True)  # $3,100 every two weeks
    assert rows["I-200-24004-000016"] == ("Non-tech", 85_800, True)  # $1,650 a week
    assert rows["I-200-24006-000018"][1] is None  # $5M a year is a typo, not a wage
    assert rows["I-200-24100-000021"][0] == "Product"
    assert rows["I-200-24130-000022"][0] == "Data"


def test_each_matching_rule(warehouse):
    rows = warehouse.sql(
        """select company, employer_name, employer_zip5, match_rule, tier
           from int_matches order by company, match_rule"""
    ).fetchall()
    assert rows == [
        # legal suffix differs (Corp / Corporation), same ZIP
        ("Marrowgate Health Corp", "Marrowgate Health Corporation", "94301", 1, "high"),
        ("Marrowgate Health Corp", "Marrowgate Health", "90012", 3, "medium"),
        ("Nimbus Thistle AI, Inc.", "Nimbus Thistle AI, Inc.", "94704", 1, "high"),
        ("Quillfern Robotics, Inc.", "QUILLFERN ROBOTICS INC", "94107", 1, "high"),
        ("Quillfern Robotics, Inc.", "Quillfern Robotics Inc.", "94612", 2, "high"),
        ("Quillfern Robotics, Inc.", "Quillfern Robotic Inc", "94105", 4, "medium"),
    ]


def test_generic_name_does_not_match_outside_its_zip(warehouse):
    generic = warehouse.sql(
        "select is_generic from int_name_keys where source = 'formd' and name_key = 'nova'"
    ).fetchone()[0]
    assert generic
    assert not warehouse.sql("select 1 from int_matches where company = 'Nova, Inc.'").fetchall()
    assert not warehouse.sql("select 1 from int_match_conflicts").fetchall()


def test_events_are_lcas_of_matched_employers(warehouse):
    rows = warehouse.sql(
        """select companies.company, count(*)
           from fct_lca_events as events
           inner join dim_company as companies using (cik)
           group by 1 order by 1"""
    ).fetchall()
    # Ferrowmont (never raised), Brindlewood (Texas) and the other Nova contribute nothing.
    assert rows == [
        ("Marrowgate Health Corp", 3),
        ("Nimbus Thistle AI, Inc.", 3),
        ("Quillfern Robotics, Inc.", 9),
    ]


def test_match_quality_has_a_row_per_rule_in_use(warehouse):
    rows = warehouse.sql(
        "select match_rule, pairs from mart_match_quality where scope = 'rule' order by 1"
    ).fetchall()
    assert rows == [(1, 3), (2, 1), (3, 1), (4, 1)]
    matched, total = warehouse.sql(
        "select startups, all_startups from mart_match_quality where scope = 'overall'"
    ).fetchone()
    assert (matched, total) == (3, 4)


def test_raise_windows(warehouse):
    rows = {
        accession: rest
        for accession, *rest in warehouse.sql(
            """select accession, prior_24m, after_12m, after_12m_new_hire, days_to_first_lca,
                      has_full_followup
               from fct_raises"""
        ).fetchall()
    }
    # Quillfern's first raise: one LCA in the two years before, eight in the year after
    assert rows["0009000001-23-000001"] == [1, 8, 7, 28, True]
    # its second raise: the six earlier LCAs are now "before"
    assert rows["0009000001-24-000003"] == [6, 3, 3, 50, True]
    assert rows["0009000004-23-000001"] == [0, 3, 3, 80, True]  # Marrowgate
    assert rows["0009000007-24-000001"] == [0, 3, 3, 20, True]  # Nimbus
    assert rows["0009000010-24-000001"] == [0, 0, 0, None, True]  # Nova never files
    # the 2025 raise has less than a year of LCA data after it
    assert rows["0009000004-25-000002"] == [3, 0, 0, None, False]


def test_known_rates(warehouse):
    """The fixture is small enough to work the rates out by hand."""
    one = lambda sql: warehouse.sql(sql).fetchall()  # noqa: E731
    # five raises have a full year of follow-up; four were followed by an H-1B filing
    assert one("select metric, n, sponsored, sponsor_rate from mart_sponsor_rate order by 1") == [
        ("any", 5, 4, 0.8),
        ("new_hire", 5, 4, 0.8),
    ]
    assert one("select round_bin, n, sponsored from mart_by_round order by round_order") == [
        ("<$2M", 1, 1),
        ("$2–10M", 2, 1),
        ("$10–50M", 1, 1),
        ("unknown", 1, 1),
    ]
    assert one("select history, n, sponsored from mart_by_history order by 1") == [
        ("no_prior", 3, 2),
        ("sponsored_before", 2, 2),
    ]
    assert one("select n, with_entry_level from mart_entry_level") == [(3, 3)]
    assert one("select distinct n, median_days from mart_time_to_lca") == [(4, 39.0)]
    assert one("select bucket, raises from mart_time_to_lca order by bucket_order")[:3] == [
        ("0–30", 2),
        ("31–60", 1),
        ("61–90", 1),
    ]
    # Bay Area H-1B employers: Quillfern (two spellings), Nimbus, Marrowgate, Ferrowmont
    assert one("select n, startup_employers, lcas, startup_lcas from mart_market_share") == [
        (5, 4, 15, 14)
    ]


def test_post_raise_lcas_are_counted_once(warehouse):
    total, distinct = warehouse.sql(
        "select count(*), count(distinct case_number) from int_post_raise_lcas"
    ).fetchone()
    assert total == distinct == 14
