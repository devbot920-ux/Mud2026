class_name WorldLoader
extends RefCounted

const CONTRACT_NAME := "mud2026.engine-neutral-world"
const CONTRACT_VERSION := "1.0.0"
const EXPECTED_COUNTS := {
	"rooms": 63,
	"edges": 130,
	"doors": 2,
	"npcs": 18,
	"items": 12,
	"spawns": 19,
	"modifiers": 70,
}


static func fixture_path_from_arguments() -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--fixture="):
			return argument.trim_prefix("--fixture=")
	var environment_path := OS.get_environment("MUD2026_FIXTURE_PATH")
	if not environment_path.is_empty():
		return environment_path
	return "res://local/pendelhaven-v1.json"


static func load_fixture(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {"ok": false, "errors": ["Fixture not found: %s" % path], "world": {}}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {"ok": false, "errors": ["Cannot open fixture: %s" % path], "world": {}}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if not parsed is Dictionary:
		return {"ok": false, "errors": ["Fixture root must be a JSON object"], "world": {}}
	var world: Dictionary = parsed
	var errors := validate(world)
	return {"ok": errors.is_empty(), "errors": errors, "world": world}


static func validate(world: Dictionary) -> Array[String]:
	var errors: Array[String] = []
	var contract: Dictionary = world.get("contract", {})
	if contract.get("name", "") != CONTRACT_NAME:
		errors.append("Unsupported contract name")
	if contract.get("version", "") != CONTRACT_VERSION:
		errors.append("Unsupported contract version")
	for family: String in EXPECTED_COUNTS:
		var records: Variant = world.get(family, null)
		if not records is Array:
			errors.append("%s must be an array" % family)
		elif records.size() != EXPECTED_COUNTS[family]:
			errors.append("%s count is %d; expected %d" % [family, records.size(), EXPECTED_COUNTS[family]])
	_validate_references(world, errors)
	_validate_fixture_boundary(world, errors)
	return errors


static func _validate_references(world: Dictionary, errors: Array[String]) -> void:
	var room_ids := _id_set(world.get("rooms", []))
	var npc_ids := _id_set(world.get("npcs", []))
	var item_ids := _id_set(world.get("items", []))
	var edge_ids: Dictionary = {}
	for edge: Variant in world.get("edges", []):
		if not edge is Dictionary:
			errors.append("Edge entry must be an object")
			continue
		var edge_record: Dictionary = edge
		var edge_id: Variant = edge_record.get("id")
		if edge_ids.has(edge_id):
			errors.append("Duplicate edge ID: %s" % str(edge_id))
		edge_ids[edge_id] = true
		if not room_ids.has(edge_record.get("from_room")):
			errors.append("Edge %s has unknown source room" % str(edge_id))
		if not room_ids.has(edge_record.get("to_room")):
			errors.append("Edge %s has unknown destination room" % str(edge_id))
	for spawn: Variant in world.get("spawns", []):
		if not spawn is Dictionary:
			continue
		var spawn_record: Dictionary = spawn
		if not room_ids.has(spawn_record.get("id")):
			errors.append("Spawn %s has no matching room" % str(spawn_record.get("id")))
		for entry: Variant in spawn_record.get("entries", []):
			if not entry is Dictionary:
				continue
			var entry_record: Dictionary = entry
			var entity_id: Variant = entry_record.get("entity_id")
			match entry_record.get("entity_type", ""):
				"npc":
					if not npc_ids.has(entity_id):
						errors.append("Spawn references unknown NPC %s" % str(entity_id))
				"item":
					if not item_ids.has(entity_id):
						errors.append("Spawn references unknown item %s" % str(entity_id))
				_:
					errors.append("Spawn has unknown entity type")


static func _validate_fixture_boundary(world: Dictionary, errors: Array[String]) -> void:
	var fixture: Dictionary = world.get("fixture", {})
	var primary: Array = fixture.get("primary_room_ids", [])
	var stubs: Array = fixture.get("stub_room_ids", [])
	if primary.size() != 60:
		errors.append("Fixture must identify 60 primary rooms")
	if stubs.size() != 3:
		errors.append("Fixture must identify 3 boundary stubs")
	var west_pair := 0
	for edge: Variant in world.get("edges", []):
		if edge is Dictionary and edge.get("direction") == "W":
			if (edge.get("from_room") == 4057 and edge.get("to_room") == 4058) or (edge.get("from_room") == 4058 and edge.get("to_room") == 4057):
				west_pair += 1
	if west_pair != 2:
		errors.append("The 4057/4058 same-west edge pair was not preserved")


static func _id_set(records: Array) -> Dictionary:
	var result: Dictionary = {}
	for record: Variant in records:
		if record is Dictionary:
			result[record.get("id")] = true
	return result


static func field_value(record: Dictionary, field_name: String, fallback: Variant = null) -> Variant:
	for field: Variant in record.get("fields", []):
		if field is Dictionary and field.get("name", "") == field_name:
			return field.get("value", fallback)
	return fallback


static func field_confidence(record: Dictionary, field_name: String) -> String:
	for field: Variant in record.get("fields", []):
		if field is Dictionary and field.get("name", "") == field_name:
			return field.get("confidence", "unknown")
	return "unknown"
