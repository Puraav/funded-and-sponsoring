{#-
    Turn a company name into a matching key:
    lower case → drop a trailing state tag (/DE/) → "&" to "and" → drop dots and apostrophes
    → other punctuation to spaces → collapse spaces → drop a leading "the"
    → drop legal suffixes at the end (inc, llc, corp, ...). Words like labs, ai and
    technologies are kept: they tell companies apart.
-#}
{% macro normalise_name(col) -%}
{%- set suffixes = 'inc|incorporated|corp|corporation|co|company|llc|l l c|ltd|limited|pbc|plc|lp' -%}
nullif(
    trim(
        regexp_replace(
            regexp_replace(
                trim(
                    regexp_replace(
                        regexp_replace(
                            regexp_replace(
                                regexp_replace(
                                    regexp_replace(
                                        lower(strip_accents({{ col }})),
                                        '\s*[/\\]\s*[a-z]{2}\s*[/\\]?\s*$', ''
                                    ),
                                    '&', ' and ', 'g'
                                ),
                                '[.''’`]', '', 'g'
                            ),
                            '[^a-z0-9]+', ' ', 'g'
                        ),
                        '\s+', ' ', 'g'
                    )
                ),
                '^the ', ''
            ),
            '( ({{ suffixes }}))+$', ''
        )
    ),
    ''
)
{%- endmacro %}
