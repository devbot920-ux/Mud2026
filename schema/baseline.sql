PRAGMA foreign_keys = ON;

CREATE TABLE source_file (
  source_file_id INTEGER PRIMARY KEY,
  logical_name TEXT NOT NULL UNIQUE,
  file_name TEXT NOT NULL,
  byte_length INTEGER NOT NULL,
  sha256 TEXT NOT NULL CHECK(length(sha256) = 64)
);
CREATE TABLE schema_object (
  schema_object_id INTEGER PRIMARY KEY,
  source_file_id INTEGER NOT NULL REFERENCES source_file,
  object_type TEXT NOT NULL, object_name TEXT NOT NULL, table_name TEXT NOT NULL,
  sql_text TEXT,
  UNIQUE(source_file_id, object_type, object_name)
);
CREATE TABLE source_row (
  source_row_id INTEGER PRIMARY KEY,
  source_file_id INTEGER NOT NULL REFERENCES source_file,
  table_name TEXT NOT NULL, source_ordinal INTEGER NOT NULL,
  source_identity_json TEXT NOT NULL, record_sha256 TEXT NOT NULL,
  UNIQUE(source_file_id, table_name, source_ordinal)
);
CREATE TABLE source_value (
  source_value_id INTEGER PRIMARY KEY,
  source_row_id INTEGER NOT NULL REFERENCES source_row,
  column_ordinal INTEGER NOT NULL, column_name TEXT NOT NULL,
  storage_class TEXT NOT NULL CHECK(storage_class IN ('null','integer','real','text','blob')),
  integer_value INTEGER, real_value REAL, text_value TEXT, blob_value BLOB,
  byte_length INTEGER, value_sha256 TEXT NOT NULL,
  UNIQUE(source_row_id, column_ordinal)
);
CREATE TABLE decoded_entity (
  decoded_entity_id INTEGER PRIMARY KEY, entity_type TEXT NOT NULL,
  stable_id TEXT NOT NULL, source_row_id INTEGER NOT NULL REFERENCES source_row,
  UNIQUE(entity_type, stable_id, source_row_id)
);
CREATE TABLE decoded_field (
  decoded_field_id INTEGER PRIMARY KEY,
  decoded_entity_id INTEGER NOT NULL REFERENCES decoded_entity,
  source_row_id INTEGER NOT NULL REFERENCES source_row,
  field_name TEXT NOT NULL, value_json TEXT NOT NULL,
  byte_offset INTEGER, byte_width INTEGER, decoding_rule TEXT NOT NULL,
  confidence TEXT NOT NULL CHECK(confidence IN ('confirmed','strong','tentative','unknown')),
  UNIQUE(decoded_entity_id, field_name, byte_offset)
);
CREATE TABLE topology_edge (
  topology_edge_id INTEGER PRIMARY KEY, from_room INTEGER NOT NULL,
  direction TEXT NOT NULL, to_room INTEGER NOT NULL,
  door INTEGER NOT NULL, hidden INTEGER NOT NULL,
  direction_offset INTEGER NOT NULL, target_offset INTEGER NOT NULL,
  hidden_source_row_id INTEGER REFERENCES source_row,
  source_row_id INTEGER NOT NULL REFERENCES source_row,
  UNIQUE(from_room, direction, to_room, door, source_row_id, direction_offset, target_offset)
);
CREATE TABLE mod1_tag_catalog (
  tag INTEGER, tag_hex TEXT, record_count INTEGER NOT NULL,
  truncated_count INTEGER NOT NULL, offset_assumption INTEGER NOT NULL,
  PRIMARY KEY(tag, offset_assumption)
);
CREATE TABLE import_run (
  singleton INTEGER PRIMARY KEY CHECK(singleton=1), schema_version INTEGER NOT NULL,
  semantic_sha256 TEXT NOT NULL, source_count INTEGER NOT NULL,
  row_count INTEGER NOT NULL, value_count INTEGER NOT NULL
);
