import type { Metadata } from "next";
import { PageTitle, Section, tableClass, tdClass, thClass } from "@/components/ui";
import { loadFindings } from "@/lib/data";
import { count, day, pct } from "@/lib/format";
import { REPO_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "Method",
  description:
    "Data sources, definitions, match quality and limitations behind Funded & Sponsoring.",
  openGraph: { title: "Method · Funded & Sponsoring" },
};

export default function MethodPage() {
  const { coverage, match_quality: quality } = loadFindings();
  return (
    <>
      <PageTitle
        title="Method"
        lead="Two public datasets, joined on company name and address. Everything is reproducible from the code."
      />

      <Section title="Sources">
        <ul className="max-w-3xl list-disc space-y-2 pl-5">
          <li>
            <a
              href="https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets"
              className="underline"
            >
              SEC Form D data sets
            </a>
            : the notice a company files after selling securities privately. It gives who
            raised, when, how much and where. {count(coverage.raises)} raises by{" "}
            {count(coverage.companies)} startups, {day(coverage.first_raise)} to{" "}
            {day(coverage.last_raise)}.
          </li>
          <li>
            <a
              href="https://www.dol.gov/agencies/eta/foreign-labor/performance"
              className="underline"
            >
              Department of Labor LCA disclosure data
            </a>
            : every Labor Condition Application, the wage filing an employer makes before an
            H-1B petition. It gives the employer, job, worksite and offered wage. Covered to{" "}
            {day(coverage.lca_data_through)}.
          </li>
          <li>
            <a
              href="https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.2020.html"
              className="underline"
            >
              Census 2020 ZIP-to-county relationship file
            </a>
            , to decide which ZIP codes are in the Bay Area.
          </li>
        </ul>
      </Section>

      <Section title="Definitions">
        <dl className="max-w-3xl space-y-3">
          {[
            ["Bay Area", "The nine counties: Alameda, Contra Costa, Marin, Napa, San Francisco, San Mateo, Santa Clara, Solano and Sonoma. A ZIP code belongs to the county holding most of its land."],
            ["Startup raise", "An original Form D (not an amendment) from a Bay Area operating company. Funds, SPVs, real-estate vehicles, mergers, companies already registered with the SEC (listed companies) and two long-established firms are left out."],
            ["Sponsoring event", "A certified H-1B LCA whose employer matches the startup. Cases later withdrawn are not counted."],
            ["Followed by a filing", "At least one sponsoring event on the day of the Form D or in the 12 months after. Only raises with a full year of LCA data after them count in the rates."],
            ["New-hire filing", "An LCA for a worker new to the employer, not an extension for a current one."],
            ["Early-career tech role", "A software, data or product job at prevailing wage Level I or II."],
            ["Offered wage", "The bottom of the wage range on the LCA, converted to a yearly figure."],
          ].map(([term, meaning]) => (
            <div key={term}>
              <dt className="font-medium">{term}</dt>
              <dd className="text-zinc-700 dark:text-zinc-300">{meaning}</dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section title="Match quality">
        <p className="max-w-3xl">
          {count(quality.matched)} of {count(quality.startups)} startups (
          {pct(quality.match_rate)}) were matched to an H-1B employer. Names are normalised
          (case, punctuation, legal suffixes) and then matched by four rules, strictest first.
          A sample of {quality.labelled} matches was checked against the street addresses on both
          filings and against public sources; {quality.labelled_correct} were correct.
        </p>
        <div className="mt-4 overflow-x-auto">
          <table className={tableClass}>
            <thead>
              <tr>
                <th scope="col" className={thClass}>Rule</th>
                <th scope="col" className={thClass}>Confidence</th>
                <th scope="col" className={`${thClass} text-right`}>Matched pairs</th>
                <th scope="col" className={`${thClass} text-right`}>Checked</th>
                <th scope="col" className={`${thClass} text-right`}>Correct</th>
              </tr>
            </thead>
            <tbody>
              {quality.by_rule.map((rule) => (
                <tr key={rule.rule}>
                  <td className={tdClass}>{rule.name}</td>
                  <td className={tdClass}>{rule.tier}</td>
                  <td className={`${tdClass} text-right tabular-nums`}>{count(rule.pairs)}</td>
                  <td className={`${tdClass} text-right tabular-nums`}>{rule.labelled}</td>
                  <td className={`${tdClass} text-right tabular-nums`}>{rule.labelled_correct}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 max-w-3xl text-sm text-zinc-600 dark:text-zinc-400">
          The samples per rule are small, so read the precision as &ldquo;no errors found&rdquo;,
          not as a guarantee. The check was done with AI assistance and is documented row by row
          in the repository.
        </p>
      </Section>

      <Section title="The radar score">
        <div id="radar" className="max-w-3xl scroll-mt-8">
          <p>
            The quarterly Form D data sets lag by up to three months, so the radar reads new
            filings straight from SEC EDGAR each week and scores each startup from 0 to 100:
          </p>
          <ul className="mt-3 list-disc space-y-1 pl-5">
            <li>up to 40 points for H-1B filings in the last 24 months (more filings, more points, levelling off)</li>
            <li>25 points if any were for software, data or product roles</li>
            <li>15 points if any were at Level I or II (early-career)</li>
            <li>up to 20 points for the amount raised</li>
          </ul>
          <p className="mt-3">
            A high score means the company has sponsored recently and just raised money. It does
            not mean it has open roles or will sponsor again.
          </p>
        </div>
      </Section>

      <Section title="Limitations">
        <ul className="max-w-3xl list-disc space-y-2 pl-5">
          <li>An LCA is an application step, not an approved H-1B or an actual hire.</li>
          <li>Form D is filed by many but not all startups; some file late or not at all.</li>
          <li>
            Matching relies on legal names. A startup that files LCAs under a different name, or
            from outside California, is missed and counted as not filing, so the rates are a
            floor.
          </li>
          <li>Form D amounts are self-reported.</li>
          <li>
            LCA data starts in October 2022, so &ldquo;the 24 months before&rdquo; is only 12 to
            24 months for raises made in late 2023.
          </li>
          <li>
            These are associations. A raise followed by a filing does not show that the money
            caused the filing.
          </li>
        </ul>
        <p className="mt-4">
          <a href={REPO_URL} className="underline">
            Code, tests and build notes on GitHub
          </a>
          .
        </p>
      </Section>
    </>
  );
}
