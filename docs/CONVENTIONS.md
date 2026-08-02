# Project Conventions

## Evidence grades

Use one of these exact values in structured output:

- `confirmed`: authoritative code behavior or repeatable independent validation establishes the meaning.
- `strong`: structure and corroborating evidence consistently support the meaning; no known contradiction.
- `tentative`: useful working hypothesis, but another plausible interpretation remains.
- `unknown`: preserved evidence with no asserted semantic meaning.

Moving a field to a higher confidence requires recording the evidence in a commit, research note, test, or data-dictionary entry.

## Provenance

Decoded values should eventually retain:

- source file identity from the source manifest
- source database and table
- source row ID and available keys
- record type/tag, when applicable
- byte offset and width or decoding rule
- raw value or raw-record reference
- decoder version
- confidence
- optional evidence note

## Naming

- Python modules, functions, database tables, and fields: `snake_case`
- Stable semantic IDs: lowercase domain prefix plus source ID when feasible, such as `room:416`
- Source database names: retain original uppercase stem in provenance
- Original text: preserve decoded content separately from normalized/searchable text
- Unknown binary fields: `unknown_<offset_hex>_<width>` until evidence supports a semantic name

## Generated data

- Private or intermediate output belongs in ignored `var/`.
- Outputs must be deterministic for identical source content and tool version.
- Sort file inventories and unordered collections before serialization.
- JSON is UTF-8, uses two-space indentation, and ends with a newline.
- Never hand-edit generated data to repair decoding; fix the decoder or add a documented override.

## Validation

Every decoder should test normal records, edge cases, truncation, unknown values, and source immutability. Baseline counts are regression evidence, not proof that field interpretations are correct.
