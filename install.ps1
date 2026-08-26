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
    [string]$Tag = 'v0.9.3',
    [string]$ExpectedSha256 = '794b95deee02e0a2e0f1e22daec36a86912438d8dbdeef13fb749ea23379dee9',
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

if ($ExpectedSha256) {
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
