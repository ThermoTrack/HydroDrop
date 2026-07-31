# Build a clean HydroDrop ZIP for plugins.qgis.org submission.
# Usage: .\scripts\build_plugin_zip.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Version = (Select-String -Path "$Root\metadata.txt" -Pattern "^version=(.+)$").Matches.Groups[1].Value.Trim()
$Dist = Join-Path $Root "dist"
$Stage = Join-Path $env:TEMP "HydroDrop-pack-$Version"
$ZipName = "HydroDrop-$Version.zip"
$ZipPath = Join-Path $Dist $ZipName

$Include = @(
    "__init__.py", "hydrodrop.py", "metadata.txt", "LICENSE", "README.md",
    "requirements.txt", "resources.qrc", "icons", "engine", "gui",
    "processing"
)

if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
$Target = Join-Path $Stage "HydroDrop"
New-Item -ItemType Directory -Path $Target -Force | Out-Null

foreach ($item in $Include) {
    $src = Join-Path $Root $item
    if (-not (Test-Path $src)) {
        Write-Warning "Missing: $item"
        continue
    }
    Copy-Item $src (Join-Path $Target $item) -Recurse -Force
}

Get-ChildItem $Target -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $Target -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

New-Item -ItemType Directory -Path $Dist -Force | Out-Null
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

Compress-Archive -Path $Target -DestinationPath $ZipPath -Force
Remove-Item $Stage -Recurse -Force

Write-Host "Created: $ZipPath"
Write-Host "Upload at: https://plugins.qgis.org/publish/"
