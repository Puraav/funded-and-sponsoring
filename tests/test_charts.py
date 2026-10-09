"""charts.py draws every PNG from the marts at the size the spec asks for."""

import struct

from fundsponsor import charts


def png_size(path):
    with path.open("rb") as handle:
        header = handle.read(24)
    return struct.unpack(">II", header[16:24])


def test_all_charts_are_drawn_at_1600_by_1000(warehouse, tmp_path):
    paths = charts.run(warehouse, tmp_path)

    assert [p.name for p in paths] == [
        "01_sponsor_rate_by_round.png",
        "02_prior_history.png",
        "03_roles_and_wages.png",
        "04_entry_level.png",
        "05_days_to_first_lca.png",
        "06_match_quality.png",
    ]
    for path in paths:
        assert png_size(path) == (1600, 1000)


def test_round_bins_read_as_words():
    assert charts.plain_bin("<$2M") == "under $2M"
    assert charts.plain_bin("$50M+") == "of $50M+"
