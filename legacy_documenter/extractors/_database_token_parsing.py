"""Legacy import compatibility: pure re-exports; implementation lives in the adapter."""
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors._database_token_parsing import (
    SQL_RE,
    strip_string_literals,
    literal,
    sql_kind,
    first_sql_keyword,
    split_args,
 )
