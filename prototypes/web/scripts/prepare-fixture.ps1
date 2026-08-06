param(
  [string]$Source = "C:\code\Mud2026\var\exports\pendelhaven-v1.json",
  [string]$SpellSource = "C:\dos\modules\RCI_SPEL.db"
)
$ErrorActionPreference = "Stop"
$Expected = "146D19341A7172EFA604E7E32D9277A9E86750ADE26D5637CFDA1EDBBDDE2DA4"
$Resolved = (Resolve-Path -LiteralPath $Source).Path
$Actual = (Get-FileHash -LiteralPath $Resolved -Algorithm SHA256).Hash
if ($Actual -ne $Expected) { throw "Fixture hash mismatch. Expected $Expected but found $Actual. Refusing to copy." }
$Destination = Join-Path $PSScriptRoot "..\public\private\pendelhaven-v1.json"
New-Item -ItemType Directory -Force -Path (Split-Path $Destination) | Out-Null
Copy-Item -LiteralPath $Resolved -Destination $Destination -Force
& python (Join-Path $PSScriptRoot "..\..\..\scripts\export_spell_fixture.py") --source $SpellSource --output (Join-Path $PSScriptRoot "..\..\..\var\exports\spells-v1.json")
if ($LASTEXITCODE -ne 0) { throw "Spell fixture export failed." }
$SpellDestination = Join-Path $PSScriptRoot "..\public\private\spells-v1.json"
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "..\..\..\var\exports\spells-v1.json") -Destination $SpellDestination -Force
Write-Host "Prepared verified private fixture at $Destination"
Write-Host "Prepared source-decoded private spell fixture at $SpellDestination"
