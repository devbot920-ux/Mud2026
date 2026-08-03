extends SceneTree

const WorldLoaderScript = preload("res://src/world_loader.gd")

var failures: Array[String] = []


func _initialize() -> void:
	_test_synthetic_contract()
	var path: String = WorldLoaderScript.fixture_path_from_arguments()
	var result: Dictionary = WorldLoaderScript.load_fixture(path)
	_check(result.ok, "private corrected fixture loads and validates: %s" % str(result.errors))
	if result.ok:
		var world: Dictionary = result.world
		_check(world.rooms.size() == 63, "63 rooms")
		_check(world.edges.size() == 130, "130 edge records")
		_check(world.doors.size() == 2, "2 door sides")
		_check(world.npcs.size() == 18, "18 NPCs")
		_check(world.items.size() == 12, "12 items")
		_check(world.spawns.size() == 19, "19 spawns")
		_check(world.modifiers.size() == 70, "70 modifiers")
		var same_west: Array = world.edges.filter(func(edge: Dictionary) -> bool:
			return edge.direction == "W" and ((edge.from_room == 4057 and edge.to_room == 4058) or (edge.from_room == 4058 and edge.to_room == 4057)))
		_check(same_west.size() == 2, "4057/4058 same-west records remain separate")
		var pair_ids: Dictionary = {}
		for edge: Dictionary in same_west:
			pair_ids[edge.id] = true
		_check(pair_ids.size() == 2, "same-west records keep distinct edge IDs")
		var hidden_count: int = world.edges.filter(func(edge: Dictionary) -> bool: return edge.hidden).size()
		var boundary_count: int = world.edges.filter(func(edge: Dictionary) -> bool:
			return edge.from_room in world.fixture.stub_room_ids or edge.to_room in world.fixture.stub_room_ids).size()
		_check(hidden_count > 0, "fixture exercises hidden exits")
		_check(boundary_count == 5, "fixture preserves 5 boundary edges")
	_finish()


func _test_synthetic_contract() -> void:
	var world := _synthetic_world()
	_check(WorldLoaderScript.validate(world).is_empty(), "synthetic non-proprietary contract validates")
	var broken: Dictionary = world.duplicate(true)
	broken.edges[1].id = broken.edges[0].id
	var errors: Array[String] = WorldLoaderScript.validate(broken)
	_check(errors.any(func(error: String) -> bool: return error.begins_with("Duplicate edge ID")), "duplicate edge IDs are rejected")
	broken = world.duplicate(true)
	broken.spawns[0].entries[0].entity_id = 999999
	errors = WorldLoaderScript.validate(broken)
	_check(errors.any(func(error: String) -> bool: return error.begins_with("Spawn references unknown NPC")), "dangling spawn entities are rejected")


func _synthetic_world() -> Dictionary:
	var rooms: Array[Dictionary] = []
	var primary_ids: Array[int] = [4057, 4058]
	for index: int in range(58):
		primary_ids.append(10000 + index)
	var stub_ids: Array[int] = [20000, 20001, 20002]
	for room_id: int in primary_ids + stub_ids:
		rooms.append({"id": room_id})
	var edges: Array[Dictionary] = [
		{"id": 1, "from_room": 4057, "to_room": 4058, "direction": "W", "hidden": false, "door": true},
		{"id": 2, "from_room": 4058, "to_room": 4057, "direction": "W", "hidden": false, "door": true},
	]
	for index: int in range(128):
		var source: int = primary_ids[index % primary_ids.size()]
		var destination: int = primary_ids[(index + 1) % primary_ids.size()]
		edges.append({"id": index + 3, "from_room": source, "to_room": destination, "direction": "N", "hidden": index == 0, "door": false})
	var npcs: Array[Dictionary] = []
	for index: int in range(18):
		npcs.append({"id": 30000 + index})
	var items: Array[Dictionary] = []
	for index: int in range(12):
		items.append({"id": 40000 + index})
	var spawns: Array[Dictionary] = []
	for index: int in range(19):
		spawns.append({"id": primary_ids[index], "entries": [{"entity_type": "npc", "entity_id": 30000, "count": 1}]})
	var modifiers: Array[Dictionary] = []
	for index: int in range(70):
		modifiers.append({"source_row_id": 50000 + index})
	return {
		"contract": {"name": "mud2026.engine-neutral-world", "version": "1.0.0"},
		"fixture": {"primary_room_ids": primary_ids, "stub_room_ids": stub_ids},
		"rooms": rooms, "edges": edges, "doors": [{"id": 1}, {"id": 2}],
		"npcs": npcs, "items": items, "spawns": spawns, "modifiers": modifiers,
	}


func _check(condition: bool, label: String) -> void:
	if condition:
		print("PASS: %s" % label)
	else:
		failures.append(label)
		push_error("FAIL: %s" % label)


func _finish() -> void:
	if failures.is_empty():
		print("Godot fixture integrity suite passed")
		quit(0)
	else:
		quit(1)
