$ErrorActionPreference = "Stop"
$godot = if ($env:MUD2026_GODOT) { $env:MUD2026_GODOT } else { "C:\code\Godot\Godot_v4.7.1-stable_win64_console.exe" }
$fixture = if ($env:MUD2026_FIXTURE_PATH) { $env:MUD2026_FIXTURE_PATH } else { "C:\code\Mud2026\var\exports\pendelhaven-v1.json" }
& $godot --headless --path $PSScriptRoot -s res://tests/test_world_loader.gd -- --fixture=$fixture
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
