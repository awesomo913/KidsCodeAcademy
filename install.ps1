# Kids Code Academy — Windows installer
#
# Usage (PowerShell, no admin needed):
#   irm https://raw.githubusercontent.com/awesomo913/KidsCodeAcademy/main/install.ps1 | iex
#
# Downloads the latest release EXE, verifies SHA-256 (when pinned), saves to your
# Desktop, and launches it. No registry edits, no system changes.

[CmdletBinding()]
param(
    [string]$InstallDir = (Join-Path $env:USERPROFILE 'Desktop'),
    [string]$Tag = 'latest',
    [string]$ExpectedSha256 = 'b928523abcb921219e60a134df254e5c461e82a3f59cc34449fd6600be40374e',
    [switch]$NoLaunch
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # speeds up Invoke-WebRequest dramatically

$exeName = 'KidsCodeAcademy.exe'
if ($Tag -eq 'latest') {
    $url = "https://github.com/awesomo913/KidsCodeAcademy/releases/latest/download/$exeName"
} else {
    $url = "https://github.com/awesomo913/KidsCodeAcademy/releases/download/$Tag/$exeName"
}

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
$dest = Join-Path $InstallDir $exeName

Write-Host "[KidsCodeAcademy] downloading $exeName ..." -ForegroundColor Cyan
Write-Host "  from: $url"
Write-Host "  to:   $dest"

Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing

if ($ExpectedSha256 -and $Tag -eq 'v0.1.0') {
    Write-Host "[KidsCodeAcademy] verifying SHA-256 ..." -ForegroundColor Cyan
    $actual = (Get-FileHash -Path $dest -Algorithm SHA256).Hash.ToLower()
    if ($actual -ne $ExpectedSha256.ToLower()) {
        Remove-Item $dest -Force
        throw "SHA-256 mismatch. Expected $ExpectedSha256, got $actual. File deleted for safety."
    }
    Write-Host "[KidsCodeAcademy] hash OK." -ForegroundColor Green
}

Write-Host "[KidsCodeAcademy] installed at $dest" -ForegroundColor Green

if (-not $NoLaunch) {
    Write-Host "[KidsCodeAcademy] launching ..." -ForegroundColor Cyan
    Start-Process -FilePath $dest
}
