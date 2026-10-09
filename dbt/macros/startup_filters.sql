{#-
    The rules that separate an operating startup from a fund, an SPV, a property deal or a
    buyout vehicle. Shared by the quarterly raises and the weekly radar so they cannot drift.
    `rel` is the relation alias; it must have industry, company, entity_type and
    is_business_combination columns.
-#}
{% macro startup_filters(rel) -%}
{{ rel }}.industry not in (select industry_group from {{ ref('excluded_industry_groups') }})
    and not {{ is_fund_name(rel ~ '.company') }}
    -- mergers and buyouts are filed on Form D too, but they are not fundraises
    and not {{ rel }}.is_business_combination
    -- venture-backed startups are corporations; partnerships are funds, and an LLC that
    -- files under the catch-all "Other" industry is nearly always an SPV or a property deal
    and {{ rel }}.entity_type is distinct from 'Limited Partnership'
    and not ({{ rel }}.entity_type = 'Limited Liability Company' and {{ rel }}.industry = 'Other')
    and {{ rel }}.cik not in (select cik from {{ ref('not_startups') }})
{%- endmacro %}
