import type { Metadata } from "next";
import Link from "next/link";
import { MonthlyBars } from "@/components/MonthlyBars";
import { Section, Stat, tableClass, tdClass, thClass } from "@/components/ui";
import { loadCompanies, loadCompany, loadRadar, secCompanyUrl, secFilingUrl } from "@/lib/data";
import { city, count, day, money, usd } from "@/lib/format";

export const dynamicParams = false;

export function generateStaticParams() {
  const slugs = new Set(
    loadCompanies()
      .filter((company) => company.has_page)
      .map((company) => company.slug),
  );
  for (const row of loadRadar().rows) if (row.slug) slugs.add(row.slug);
  return [...slugs].map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: PageProps<"/company/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const company = loadCompany(slug);
  const description = `${company.name} raised ${money(company.total_sold)} across ${company.raises} Form D filing${company.raises === 1 ? "" : "s"} and has ${count(company.lcas_total)} certified H-1B LCA${company.lcas_total === 1 ? "" : "s"} on record.`;
  return {
    title: company.name,
    description,
    openGraph: { title: `${company.name} · Funded & Sponsoring`, description },
  };
}

export default async function CompanyPage({ params }: PageProps<"/company/[slug]">) {
  const { slug } = await params;
  const company = loadCompany(slug);

  return (
    <>
      <p className="text-sm">
        <Link href="/explore" className="underline">
          ← All startups
        </Link>
      </p>
      <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">{company.name}</h1>
      <p className="mt-2 text-zinc-700 dark:text-zinc-300">
        {city(company.city)}, {company.county} County · {company.industry ?? "Industry not given"}
      </p>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Stat
          value={money(company.total_sold)}
          label={`raised across ${company.raises} Form D filing${company.raises === 1 ? "" : "s"}`}
          note={`since ${day(company.first_raise)}, self-reported`}
        />
        <Stat
          value={count(company.lcas_total)}
          label="certified H-1B LCAs on record"
          note={
            company.first_lca_date
              ? `${day(company.first_lca_date)} to ${day(company.latest_lca_date)}`
              : "none matched in the data"
          }
        />
        <Stat
          value={usd(company.median_wage)}
          label="median offered wage"
          note="annualised, across those filings"
        />
      </div>

      <Section title="Raises">
        <div className="overflow-x-auto">
          <table className={tableClass}>
            <thead>
              <tr>
                <th scope="col" className={thClass}>Filed</th>
                <th scope="col" className={`${thClass} text-right`}>Amount sold</th>
                <th scope="col" className={`${thClass} text-right`}>H-1B filings, 24 mo before</th>
                <th scope="col" className={`${thClass} text-right`}>H-1B filings, 12 mo after</th>
                <th scope="col" className={thClass}>SEC filing</th>
              </tr>
            </thead>
            <tbody>
              {company.raise_list.map((raise) => (
                <tr key={raise.accession}>
                  <td className={`${tdClass} whitespace-nowrap`}>{day(raise.filing_date)}</td>
                  <td className={`${tdClass} text-right tabular-nums`}>
                    {money(raise.amount_sold)}
                  </td>
                  <td className={`${tdClass} text-right tabular-nums`}>{raise.prior_24m}</td>
                  <td className={`${tdClass} text-right tabular-nums`}>
                    {raise.after_12m}
                    {raise.has_full_followup ? "" : " so far"}
                  </td>
                  <td className={tdClass}>
                    <a href={secFilingUrl(company.cik, raise.accession)} className="underline">
                      Form D
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          &ldquo;So far&rdquo; marks a raise with less than a year of LCA data after it.{" "}
          <a href={secCompanyUrl(company.cik)} className="underline">
            All Form D filings on SEC EDGAR
          </a>
          .
        </p>
      </Section>

      {company.monthly_lcas.length ? (
        <Section title="H-1B filings by month">
          <MonthlyBars
            months={company.monthly_lcas}
            raises={company.raise_list.map((raise) => raise.filing_date)}
          />
        </Section>
      ) : null}

      {company.roles.length ? (
        <Section title="Roles and wages">
          <div className="overflow-x-auto">
            <table className={tableClass}>
              <thead>
                <tr>
                  <th scope="col" className={thClass}>Role group</th>
                  <th scope="col" className={`${thClass} text-right`}>Filings</th>
                  <th scope="col" className={`${thClass} text-right`}>Early-career (Level I–II)</th>
                  <th scope="col" className={`${thClass} text-right`}>Median wage</th>
                  <th scope="col" className={`${thClass} text-right`}>Range</th>
                </tr>
              </thead>
              <tbody>
                {company.roles.map((role) => (
                  <tr key={role.role_group}>
                    <td className={tdClass}>{role.role_group}</td>
                    <td className={`${tdClass} text-right tabular-nums`}>{role.lcas}</td>
                    <td className={`${tdClass} text-right tabular-nums`}>
                      {role.early_career_lcas}
                    </td>
                    <td className={`${tdClass} text-right tabular-nums`}>
                      {usd(role.median_wage)}
                    </td>
                    <td className={`${tdClass} text-right tabular-nums whitespace-nowrap`}>
                      {usd(role.min_wage)} to {usd(role.max_wage)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      ) : null}

      {company.officers.length ? (
        <Section title="Executive officers on the latest Form D">
          <ul className="grid grid-cols-1 gap-x-8 gap-y-1 sm:grid-cols-2">
            {company.officers.map((officer) => (
              <li key={officer.name}>
                {officer.name}
                <span className="text-sm text-zinc-600 dark:text-zinc-400">
                  {" "}
                  · {officer.relationships}
                </span>
              </li>
            ))}
          </ul>
        </Section>
      ) : null}

      <p className="mt-10 max-w-3xl text-sm text-zinc-600 dark:text-zinc-400">
        H-1B filings are matched to this company by name and address, so a filing made under a
        different legal name can be missing. An LCA is an application step before an H-1B
        petition, not an approved visa or a hire. <Link href="/method" className="underline">Method</Link>.
      </p>
    </>
  );
}
