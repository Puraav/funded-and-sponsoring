import type { Metadata } from "next";
import { Explorer } from "@/components/Explorer";
import { PageTitle } from "@/components/ui";
import { loadCompanies } from "@/lib/data";

export const metadata: Metadata = {
  title: "Explore the startups",
  description:
    "Filter Bay Area startups that raised money by size of raise, industry, county and H-1B filing history.",
  openGraph: { title: "Explore the startups · Funded & Sponsoring" },
};

export default function ExplorePage() {
  const companies = loadCompanies();
  return (
    <>
      <PageTitle
        title="Explore the startups"
        lead="Every Bay Area startup with a Form D raise since October 2023, with its H-1B filing history. Startups with at least one matched filing link to their own page."
      />
      <Explorer companies={companies} />
    </>
  );
}
