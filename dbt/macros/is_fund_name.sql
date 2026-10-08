{#- True when a lower-cased name matches any regex in the fund_name_patterns seed. -#}
{% macro is_fund_name(name_col) -%}
exists (
    select 1
    from {{ ref('fund_name_patterns') }} as fund_pattern
    where regexp_matches(lower({{ name_col }}), fund_pattern.pattern)
)
{%- endmacro %}
