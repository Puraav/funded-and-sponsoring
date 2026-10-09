// Types for the JSON files written by `python -m fundsponsor.export_site`, and loaders that
// read them from public/data at build time.
import { readFileSync } from "node:fs";
import path from "node:path";

export type Finding = {
  id: string;
  text: string;
  numbers: Record<string, unknown>;
  n: number;
  small_sample: boolean;
};

export type MatchRule = {
  rule: number;
  name: string;
  tier: string;
  pairs: number;
  startups: number;
  labelled: number;
  labelled_correct: number;
  precision: number | null;
  small_sample: boolean;
};

export type MatchQuality = {
  text: string;
  startups: number;
  matched: number;
  match_rate: number;
  labelled: number;
  labelled_correct: number;
  precision: number;
  by_rule: MatchRule[];
};

export type Findings = {
  question: string;
  coverage: {
    raises: number;
    companies: number;
    first_raise: string;
    last_raise: string;
    last_raise_with_full_followup: string;
    lca_data_through: string;
  };
  findings: Finding[];
  match_quality: MatchQuality;
};

export type RateRow = { n: number; sponsored: number; sponsor_rate: number; small_sample: boolean };

export type Metrics = {
  mart_sponsor_rate: (RateRow & { metric: string; metric_label: string })[];
  mart_by_round: (RateRow & { round_bin: string; median_lcas_per_sponsor: number | null })[];
  mart_by_history: (RateRow & { history: string; history_label: string })[];
  mart_by_industry: (RateRow & { industry: string })[];
  mart_roles_wages: {
    role_group: string;
    wage_level: string;
    n: number;
    share_of_lcas: number | null;
    median_wage: number | null;
    small_sample: boolean;
  }[];
  mart_entry_level: {
    n: number;
    with_entry_level: number;
    entry_level_share: number;
    small_sample: boolean;
  }[];
  mart_time_to_lca: {
    bucket: string;
    raises: number;
    share: number;
    n: number;
    median_days: number;
    p25_days: number;
    p75_days: number;
  }[];
  mart_market_share: {
    n: number;
    startup_employers: number;
    employer_share: number;
    lcas: number;
    startup_lcas: number;
    lca_share: number;
  }[];
};

export type Company = {
  slug: string;
  name: string;
  city: string | null;
  county: string;
  industry: string | null;
  latest_raise: string;
  raises: number;
  total_sold: number | null;
  round_bin: string;
  prior_24m: number;
  after_12m: number;
  sponsored_before: boolean;
  has_full_followup: boolean;
  lcas_total: number;
  median_wage: number | null;
  role_groups: string | null;
  has_page: boolean;
};

export type CompanyProfile = {
  cik: string;
  slug: string;
  name: string;
  city: string | null;
  county: string;
  industry: string | null;
  first_raise: string;
  latest_raise: string;
  raises: number;
  total_sold: number | null;
  lcas_total: number;
  median_wage: number | null;
  first_lca_date: string | null;
  latest_lca_date: string | null;
  raise_list: {
    accession: string;
    filing_date: string;
    first_sale_date: string | null;
    amount_sold: number | null;
    amount_offered: number | null;
    round_bin: string;
    prior_24m: number;
    after_12m: number;
    has_full_followup: boolean;
  }[];
  monthly_lcas: { month: string; lcas: number; new_hire_lcas: number }[];
  roles: {
    role_group: string;
    lcas: number;
    early_career_lcas: number;
    median_wage: number | null;
    min_wage: number | null;
    max_wage: number | null;
  }[];
  officers: { name: string; relationships: string }[];
};

export type RadarRow = {
  rank: number;
  accession: string;
  cik: string;
  company: string;
  slug: string | null;
  city: string | null;
  county: string;
  industry: string | null;
  filing_date: string;
  amount_sold: number | null;
  round_bin: string;
  score: number;
  reasons: string;
  lcas_24m: number;
  sec_url: string;
};

export type Radar = { generated: string | null; days: number | null; rows: RadarRow[] };

function load<T>(file: string): T {
  return JSON.parse(readFileSync(path.join(process.cwd(), "public", "data", file), "utf8")) as T;
}

export const loadFindings = () => load<Findings>("findings.json");
export const loadMetrics = () => load<Metrics>("metrics.json");
export const loadCompanies = () => load<Company[]>("companies.json");
export const loadRadar = () => load<Radar>("radar.json");
export const loadCompany = (slug: string) => load<CompanyProfile>(`company/${slug}.json`);

/** Links to the SEC's pages for a company and for one filing. */
export function secCompanyUrl(cik: string): string {
  return `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${cik}&type=D`;
}

export function secFilingUrl(cik: string, accession: string): string {
  return `https://www.sec.gov/Archives/edgar/data/${Number(cik)}/${accession.replaceAll("-", "")}/`;
}
