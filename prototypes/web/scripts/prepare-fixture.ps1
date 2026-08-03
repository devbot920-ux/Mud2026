param(
  [string]$Source = "C:\code\Mud2026\var\exports\pendelhaven-v1.json"
)
$ErrorActionPreference = "Stop"
$Expected = "146D19341A7172EFA604E7E32D9277A9E86750ADE26D5637CFDA1EDBBDDE2DA4"
$Resolved = (Resolve-Path -LiteralPath $Source).Path
$Actual = (Get-FileHash -LiteralPath $Resolved -Algorithm SHA256).Hash
if ($Actual -ne $Expected) { throw "Fixture hash mismatch. Expected $Expected but found $Actual. Refusing to copy." }
$Destination = Join-Path $PSScriptRoot "..\public\private\pendelhaven-v1.json"
New-Item -ItemType Directory -Force -Path (Split-Path $Destination) | Out-Null
Copy-Item -LiteralPath $Resolved -Destination $Destination -Force
Write-Host "Prepared verified private fixture at $Destination"
