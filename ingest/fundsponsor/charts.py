"""Draw the PNG charts in charts/ from the dbt marts.

Static images for the README and LinkedIn (the site draws its own interactive charts).
Every title states the finding with its number, built from the mart, never typed in.
One accent colour marks the point being made; everything else is grey.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import config  # noqa: E402
from .findings import pct, usd  # noqa: E402

ACCENT = "#2a78d6"
GREY = "#c9c8c2"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e8e7e3"
SOURCE = (
    "Source: SEC Form D, DOL LCA disclosure data · github.com/Puraav/funded-and-sponsoring"
)
SIZE = (8, 5)  # inches at 200 dpi = 1600 x 1000 px
DPI = 200

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def rows(warehouse: duckdb.DuckDBPyConnection, sql: str) -> list[dict]:
    cursor = warehouse.execute(sql)
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]


def frame(title: str, subtitle: str, *, left: float = 0.2, bottom: float = 0.13):
    """A figure with the title block on top, the source line below and one plot between."""
    figure = plt.figure(figsize=SIZE, dpi=DPI)
    title_lines = textwrap.wrap(title, 62)
    subtitle_lines = textwrap.wrap(subtitle, 100)
    y = 0.95
    figure.text(0.04, y, "\n".join(title_lines), fontsize=14, fontweight="bold", color=INK,
                va="top", linespacing=1.25)  # fmt: skip
    y -= 0.062 * len(title_lines) + 0.015
    figure.text(0.04, y, "\n".join(subtitle_lines), fontsize=9, color=MUTED, va="top",
                linespacing=1.35)  # fmt: skip
    y -= 0.042 * len(subtitle_lines) + 0.035
    figure.text(0.04, 0.03, SOURCE, fontsize=7, color=MUTED, va="bottom")
    axes = figure.add_axes((left, bottom, 0.96 - left - 0.04, y - bottom))
    axes.tick_params(length=0)
    return figure, axes


def hbars(axes, labels, values, accent_index, value_labels, *, xmax=None, percent=False):
    """Horizontal bars, first label on top, grey except the accented one."""
    positions = range(len(labels))
    colors = [ACCENT if i == accent_index else GREY for i in positions]
    axes.barh(positions, values, color=colors, height=0.56)
    axes.set_yticks(list(positions), labels)
    axes.invert_yaxis()
    limit = xmax or max(values) * 1.3
    axes.set_xlim(0, limit)
    for position, value, label in zip(positions, values, value_labels, strict=True):
        axes.text(value + limit * 0.012, position, label, va="center", fontsize=9, color=INK)
    axes.xaxis.grid(True, color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    axes.spines["left"].set_visible(False)
    axes.spines["bottom"].set_visible(False)
    if percent:
        axes.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))


def save(figure, name: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    figure.savefig(path, dpi=DPI, facecolor="white")
    plt.close(figure)
    return path


def plain_bin(round_bin: str) -> str:
    """'<$2M' → 'under $2M', '$2–10M' → 'of $2–10M', for use in a sentence."""
    return f"under {round_bin[1:]}" if round_bin.startswith("<") else f"of {round_bin}"


def chart_by_round(warehouse, out_dir: Path) -> Path:
    data = rows(warehouse, "select * from mart_by_round order by round_order")
    known = [r for r in data if r["round_bin"] != "unknown"]
    top = max(known, key=lambda r: r["sponsor_rate"])
    low = min(known, key=lambda r: r["sponsor_rate"])
    total = sum(r["n"] for r in data)
    figure, axes = frame(
        f"{pct(top['sponsor_rate'])} of {top['round_bin']} raises are followed by an H-1B "
        f"filing within a year. For raises {plain_bin(low['round_bin'])} it is "
        f"{pct(low['sponsor_rate'])}.",
        "Share of Bay Area startup raises (SEC Form D) followed by at least one certified H-1B "
        f"LCA from the same company within 12 months, by amount sold. n = {total:,} raises "
        "with a full year of follow-up.",
    )
    labels = ["Amount not reported" if r["round_bin"] == "unknown" else r["round_bin"]
              for r in data]  # fmt: skip
    hbars(
        axes,
        labels,
        [r["sponsor_rate"] for r in data],
        data.index(top),
        [f"{pct(r['sponsor_rate'])}   n = {r['n']:,}" for r in data],
        xmax=max(r["sponsor_rate"] for r in data) * 1.35,
        percent=True,
    )
    return save(figure, "01_sponsor_rate_by_round.png", out_dir)


def chart_history(warehouse, out_dir: Path) -> Path:
    data = {r["history"]: r for r in rows(warehouse, "select * from mart_by_history")}
    before, never = data["sponsored_before"], data["no_prior"]
    figure, axes = frame(
        f"Startups that sponsored before raising do it again {pct(before['sponsor_rate'])} of "
        f"the time. Those that had not: {pct(never['sponsor_rate'])}.",
        "Share of raises followed by an H-1B filing within 12 months, split by whether the "
        "company filed for H-1B workers in the 24 months before the raise. "
        f"n = {before['n'] + never['n']:,} raises.",
        left=0.34,
    )
    hbars(
        axes,
        ["Filed for H-1B workers\nbefore the raise", "No H-1B filing\nbefore the raise"],
        [before["sponsor_rate"], never["sponsor_rate"]],
        0,
        [f"{pct(r['sponsor_rate'])}   n = {r['n']:,}" for r in (before, never)],
        xmax=1.0,
        percent=True,
    )
    axes.set_ylim(1.9, -0.9)
    return save(figure, "02_prior_history.png", out_dir)


def chart_roles(warehouse, out_dir: Path) -> Path:
    data = rows(
        warehouse, "select * from mart_roles_wages where wage_level = 'All' order by n desc"
    )
    top, total = data[0], sum(r["n"] for r in data)
    figure, axes = frame(
        f"{top['role_group']} roles are {pct(top['share_of_lcas'])} of what startups file "
        f"for after raising, at a median offered wage of {usd(top['median_wage'])}.",
        "Certified H-1B LCAs filed by Bay Area startups in the 12 months after a raise, by "
        f"role group, with the median offered annual wage. n = {total:,} filings.",
        bottom=0.17,
    )
    hbars(
        axes,
        [r["role_group"] for r in data],
        [r["n"] for r in data],
        0,
        [f"{r['n']:,} filings   median {usd(r['median_wage'])}" for r in data],
        xmax=top["n"] * 1.55,
    )
    axes.set_xlabel("H-1B filings", fontsize=8)
    return save(figure, "03_roles_and_wages.png", out_dir)


def chart_entry_level(warehouse, out_dir: Path) -> Path:
    data = rows(warehouse, "select * from mart_entry_level")[0]
    share = data["entry_level_share"]
    figure, axes = frame(
        f"{pct(share)} of startups that file after raising file for an early-career tech "
        "role.",
        "Startups with at least one H-1B filing in the year after a raise. Early-career = a "
        "software, data or product role at prevailing wage Level I or II. "
        f"n = {data['n']:,} startups.",
        left=0.06,
        bottom=0.2,
    )
    axes.barh([0], [share], color=ACCENT, height=0.5)
    axes.barh([0], [1 - share - 0.004], left=[share + 0.004], color=GREY, height=0.5)
    axes.set_xlim(0, 1)
    axes.set_ylim(-0.9, 0.7)
    axes.set_yticks([])
    axes.set_xticks([])
    for spine in axes.spines.values():
        spine.set_visible(False)
    axes.text(0, -0.45, f"{pct(share)}  ({data['with_entry_level']:,} startups)\n"
              "filed for at least one early-career tech role",
              va="top", fontsize=10, color=INK, linespacing=1.4)  # fmt: skip
    axes.text(1, -0.45, f"{pct(1 - share)}  ({data['n'] - data['with_entry_level']:,} startups)\n"
              "filed only for senior or non-tech roles",
              va="top", ha="right", fontsize=10, color=MUTED, linespacing=1.4)  # fmt: skip
    return save(figure, "04_entry_level.png", out_dir)


def chart_days(warehouse, out_dir: Path) -> Path:
    summary = rows(warehouse, "select * from mart_time_to_lca order by bucket_order")[0]
    bins = rows(
        warehouse,
        """select floor(days_to_first_lca / 30) as bin, count(*) as raises
           from fct_raises
           where has_full_followup and sponsored_after
           group by 1 order by 1""",
    )
    median = summary["median_days"]
    figure, axes = frame(
        f"The first H-1B filing comes a median of {median:.0f} days after the raise; a "
        f"quarter come within {summary['p25_days']:.0f} days.",
        "Days from the SEC Form D filing to the company's first certified H-1B LCA after it, "
        "for raises followed by one within 12 months, in 30-day steps. "
        f"n = {summary['n']:,} raises.",
        left=0.09,
        bottom=0.15,
    )
    # the last step also holds days 360 to 366, so it is drawn inside the 330-360 bar
    counts: dict[int, int] = {}
    for r in bins:
        step = min(int(r["bin"]), 11)
        counts[step] = counts.get(step, 0) + r["raises"]
    starts = sorted(counts)
    axes.bar(
        [s * 30 + 15 for s in starts],
        [counts[s] for s in starts],
        width=27,
        color=[ACCENT if s == 0 else GREY for s in starts],
    )
    axes.set_xticks(range(0, 361, 60))
    axes.set_xlim(0, 366)
    axes.set_xlabel("Days after the Form D filing", fontsize=8)
    axes.set_ylabel("Raises", fontsize=8)
    axes.yaxis.grid(True, color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    axes.spines["left"].set_visible(False)
    top = max(counts.values())
    axes.set_ylim(0, top * 1.18)
    axes.axvline(median, color=INK, linewidth=1.2)
    axes.text(median + 5, top * 1.12, f"Median: {median:.0f} days", fontsize=9, color=INK,
              va="center")  # fmt: skip
    axes.text(15, counts.get(0, 0) + top * 0.025, f"{counts.get(0, 0)}", ha="center",
              fontsize=9, color=INK)  # fmt: skip
    return save(figure, "05_days_to_first_lca.png", out_dir)


def chart_match_quality(warehouse, out_dir: Path) -> Path:
    data = rows(warehouse, "select * from mart_match_quality order by match_rule")
    overall = next(r for r in data if r["scope"] == "overall")
    rules = [r for r in data if r["scope"] == "rule"]
    figure, axes = frame(
        f"{overall['startups']:,} of {overall['all_startups']:,} startups "
        f"({pct(overall['match_rate'])}) were matched to an H-1B employer. "
        f"{overall['labelled_correct']} of {overall['labelled']} checked matches were correct.",
        "Matched startup-employer pairs by matching rule, with the result of a checked "
        "sample for each rule. Rules with few checked pairs give only a rough precision.",
        left=0.3,
        bottom=0.17,
    )
    hbars(
        axes,
        [f"{r['rule_name']}\n({r['tier']} confidence)" for r in rules],
        [r["pairs"] for r in rules],
        0,
        [f"{r['pairs']:,} pair{'' if r['pairs'] == 1 else 's'}   "
         f"checked {r['labelled']}, correct {r['labelled_correct']}" for r in rules],  # fmt: skip
        xmax=max(r["pairs"] for r in rules) * 1.75,
    )
    axes.set_xlabel("Matched startup-employer pairs", fontsize=8)
    return save(figure, "06_match_quality.png", out_dir)


CHARTS = [
    chart_by_round, chart_history, chart_roles, chart_entry_level, chart_days,
    chart_match_quality,
]  # fmt: skip


def run(warehouse: duckdb.DuckDBPyConnection, out_dir: Path) -> list[Path]:
    return [chart(warehouse, out_dir) for chart in CHARTS]


def main() -> None:
    with duckdb.connect(str(config.WAREHOUSE), read_only=True) as warehouse:
        for path in run(warehouse, config.CHARTS_DIR):
            print(f"wrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
