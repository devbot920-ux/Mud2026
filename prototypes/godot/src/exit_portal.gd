class_name ExitPortal
extends Area3D

signal entered(edge_id: int)

var edge_id := -1


func configure(record: Dictionary, location: Vector3, facing: float, tint: Color) -> void:
	edge_id = int(record.get("id", -1))
	position = location
	rotation.y = facing
	collision_layer = 0
	collision_mask = 1
	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(2.4, 3.0, 1.0)
	collision.shape = shape
	add_child(collision)
	for side_x: float in [-1.15, 1.15]:
		var pillar := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = Vector3(0.28, 3.2, 0.4)
		pillar.mesh = mesh
		pillar.position = Vector3(side_x, 0.0, 0.0)
		_set_material(pillar, tint)
		add_child(pillar)
	var lintel := MeshInstance3D.new()
	var lintel_mesh := BoxMesh.new()
	lintel_mesh.size = Vector3(2.6, 0.28, 0.4)
	lintel.mesh = lintel_mesh
	lintel.position = Vector3(0.0, 1.48, 0.0)
	_set_material(lintel, tint)
	add_child(lintel)
	if record.get("door", false):
		var door := MeshInstance3D.new()
		var door_mesh := BoxMesh.new()
		door_mesh.size = Vector3(2.0, 2.8, 0.12)
		door.mesh = door_mesh
		_set_material(door, Color(0.32, 0.16, 0.06))
		add_child(door)
	body_entered.connect(_on_body_entered)


func _set_material(instance: MeshInstance3D, color: Color) -> void:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = 0.85
	instance.material_override = material


func _on_body_entered(body: Node3D) -> void:
	if body is CharacterBody3D and body.name == "Player":
		entered.emit(edge_id)
