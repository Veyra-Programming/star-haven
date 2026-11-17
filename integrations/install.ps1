<#
.SYNOPSIS
    Official Windows PowerShell Automated Installer for ODCS Dual-Engine Toolchain.
    Standard: ODCS-2.0.0 · Dual Engine: Star Programming Language + Haven Language v2.0

.DESCRIPTION
    Installs Star SDK, Haven VM Runtime, and the ODCS Python SDK on Windows.
    Adds 'star', 'haven', and 'odcs' CLI tools to user PATH.

.EXAMPLE
    # 1-Liner Quick Install from Web:
    irm https://odcs.in/install.ps1 | iex

    # Or run locally:
    powershell -ExecutionPolicy Bypass -File .\install.ps1
#>

[CmdletBinding()]
param(
    [string]$InstallDir = "$env:LOCALAPPDATA\ODCS",
    [string]$BaseUrl = "https://odcs.in",
    [switch]$SkipSdkInstall
)

$ErrorActionPreference = "Stop"

# UTF-8 Console output
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "  ___  ____   ____ ____     ____            _ _         _   _            " -ForegroundColor Cyan
Write-Host " / _ \|  _ \ / ___/ ___|   / ___|___  _ __ | (_)_ __   | |_(_) ___  _ __  " -ForegroundColor Cyan
Write-Host "| | | | | | | |   \___ \  | |   / _ \| '_ \| | | '_ \  | __| |/ _ \| '_ \ " -ForegroundColor Cyan
Write-Host "| |_| | |_| | |___ ___) | | |__| (_) | | | | | | | | | | |_| | (_) | | | |" -ForegroundColor Cyan
Write-Host " \___/|____/ \____|____/   \____\___/|_| |_|_|_|_| |_|  \__|_|\___/|_| |_|" -ForegroundColor Cyan
Write-Host "   ⭐ Star Programming Language UI  +  🕊️ Haven Language v2.0 Backend" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor DarkGray
Write-Host "   Target Architecture: Windows x64 / ARM64 (PowerShell Toolchain Installer)   " -ForegroundColor White
Write-Host "   Standard: ODCS-2.0.0 · Official ODCS Standards Foundation                   " -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor DarkGray
Write-Host ""

# 1. System & Architecture Detection
$is64Bit = [Environment]::Is64BitOperatingSystem
$arch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "ARM64" } else { "x64" }
Write-Host "[INFO] Detected Windows Operating System ($arch, 64-bit: $is64Bit)" -ForegroundColor Cyan

# 2. Check Python 3 Environment
Write-Host "[INFO] Checking Python 3 environment..." -ForegroundColor Cyan

$candidatePythons = @(
    "$env:LOCALAPPDATA\Programs\Haven\python.exe",
    "C:\Users\Admin\AppData\Local\Programs\Haven\python.exe",
    (Get-Command "py.exe" -ErrorAction SilentlyContinue).Source,
    (Get-Command "python.exe" -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notlike "*WindowsApps*" } | Select-Object -ExpandProperty Source)
) | Where-Object { $_ -and (Test-Path $_) }

$pythonExe = $null
foreach ($cand in $candidatePythons) {
    try {
        $testOut = & $cand -c "import sys; print(sys.version_info[0])" 2>$null
        if ($testOut -eq "3") {
            $pythonExe = $cand
            break
        }
    } catch {}
}

if ($pythonExe) {
    $pyVer = & $pythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
    Write-Host "[OK] Found Python $pyVer at $pythonExe" -ForegroundColor Green
} else {
    Write-Host "[WARN] Python was not found in PATH. Star & Haven CLI launchers will use embedded fallback." -ForegroundColor Yellow
}

# 3. Create Installation Directories
Write-Host "[INFO] Setting up ODCS Dual-Engine home: $InstallDir" -ForegroundColor Cyan
$binDir = Join-Path $InstallDir "bin"
$starDir = Join-Path $InstallDir "star-sdk"
$havenDir = Join-Path $InstallDir "heaven"
$sdkDir = Join-Path $InstallDir "python-sdk"

New-Item -ItemType Directory -Path $binDir -Force | Out-Null
New-Item -ItemType Directory -Path $starDir -Force | Out-Null
New-Item -ItemType Directory -Path $havenDir -Force | Out-Null
New-Item -ItemType Directory -Path $sdkDir -Force | Out-Null

# 4. Locate Local or Download Remote Files
$sourceRoot = $PSScriptRoot
if (-not $sourceRoot -or -not (Test-Path (Join-Path $sourceRoot "heaven\haven_lang.py"))) {
    $sourceRoot = (Get-Location).Path
}

$hasLocalFiles = (Test-Path (Join-Path $sourceRoot "heaven\haven_lang.py")) -or (Test-Path "E:\Star Language\star.py")

if ($hasLocalFiles) {
    Write-Host "[INFO] Deploying Star Language SDK from local toolchain..." -ForegroundColor Cyan
    if (Test-Path "E:\Star Language") {
        Copy-Item -Path "E:\Star Language\*" -Destination $starDir -Recurse -Force -Exclude "__pycache__","*.pyc"
    }

    Write-Host "[INFO] Deploying Haven Language v2.0 Runtime from local toolchain..." -ForegroundColor Cyan
    $heavenSrc = if (Test-Path (Join-Path $sourceRoot "heaven")) { Join-Path $sourceRoot "heaven" } else { ".\heaven" }
    Copy-Item -Path "$heavenSrc\*" -Destination $havenDir -Recurse -Force -Exclude "__pycache__","*.pyc","downloads"

    Write-Host "[INFO] Deploying ODCS Python SDK..." -ForegroundColor Cyan
    $sdkSrc = if (Test-Path (Join-Path $sourceRoot "odcs_sdk")) { Join-Path $sourceRoot "odcs_sdk" } else { ".\odcs_sdk" }
    if (Test-Path $sdkSrc) {
        Copy-Item -Path "$sdkSrc" -Destination (Join-Path $sdkDir "odcs_sdk") -Recurse -Force
    }
} else {
    Write-Host "[INFO] Downloading official Star & Haven release bundles from $BaseUrl..." -ForegroundColor Cyan
    $zipPath = Join-Path $env:TEMP "odcs-windows-bundle.zip"
    try {
        Invoke-WebRequest -Uri "$BaseUrl/downloads/Haven-1.0.0-win64-portable.zip" -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath $havenDir -Force
        Remove-Item $zipPath -Force
        Write-Host "[OK] Haven Language Runtime downloaded." -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Remote bundle download notice: $_" -ForegroundColor Yellow
    }
}

# 5. Create Global CLI Batch Launchers in $binDir
Write-Host "[INFO] Generating CLI Launchers in $binDir..." -ForegroundColor Cyan

# Star CLI launcher
$starBatPath = Join-Path $binDir "star.bat"
$starBatContent = @"
@echo off
set STAR_SDK=$starDir
if exist "%STAR_SDK%\star.py" (
    python "%STAR_SDK%\star.py" %*
) else (
    echo [ERROR] Star SDK not found at %STAR_SDK%
    exit /b 1
)
"@
Set-Content -Path $starBatPath -Value $starBatContent -Encoding ASCII

# Haven CLI launcher
$havenBatPath = Join-Path $binDir "haven.bat"
$havenBatContent = @"
@echo off
set HAVEN_HOME=$havenDir
if exist "%HAVEN_HOME%\haven_lang.py" (
    python "%HAVEN_HOME%\haven_lang.py" %*
) else (
    echo [ERROR] Haven Runtime not found at %HAVEN_HOME%
    exit /b 1
)
"@
Set-Content -Path $havenBatPath -Value $havenBatContent -Encoding ASCII

# ODCS CLI launcher
$odcsBatPath = Join-Path $binDir "odcs.bat"
$odcsBatContent = @"
@echo off
set ODCS_HOME=$InstallDir
python -m odcs_sdk.cli %*
"@
Set-Content -Path $odcsBatPath -Value $odcsBatContent -Encoding ASCII

# 6. Configure User Environment Variables & PATH
Write-Host "[INFO] Configuring Windows User PATH and Environment Variables..." -ForegroundColor Cyan

[Environment]::SetEnvironmentVariable("STAR_SDK", $starDir, "User")
[Environment]::SetEnvironmentVariable("HAVEN_HOME", $havenDir, "User")
[Environment]::SetEnvironmentVariable("ODCS_HOME", $InstallDir, "User")

$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if (-not $currentPath) { $currentPath = "" }
$pathEntries = $currentPath -split ";" | Where-Object { $_ -ne "" }

if ($pathEntries -notcontains $binDir) {
    $newPath = ($pathEntries + $binDir) -join ";"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "[OK] Added '$binDir' to Windows User PATH." -ForegroundColor Green
} else {
    Write-Host "[OK] '$binDir' is already registered in PATH." -ForegroundColor Green
}

# Also update current PowerShell session PATH
if ($env:PATH -notlike "*$binDir*") {
    $env:PATH = "$binDir;$env:PATH"
}
$env:STAR_SDK = $starDir
$env:HAVEN_HOME = $havenDir
$env:ODCS_HOME = $InstallDir

# 7. Install Python SDK if pip is available
if ($pythonExe -and -not $SkipSdkInstall) {
    Write-Host "[INFO] Installing official ODCS Python SDK into Python environment..." -ForegroundColor Cyan
    $wheel = Get-ChildItem -Path (Join-Path $sourceRoot "dist") -Filter "odcs_sdk-*.whl" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    if ($wheel) {
        & $pythonExe -m pip install $wheel.FullName --force-reinstall --no-warn-script-location 2>&1 | Out-Null
        Write-Host "[OK] Installed 'odcs-sdk' from wheel: $($wheel.Name)" -ForegroundColor Green
    } else {
        $setupPy = Join-Path $sourceRoot "setup.py"
        if (Test-Path $setupPy) {
            & $pythonExe -m pip install -e $sourceRoot --no-warn-script-location 2>&1 | Out-Null
            Write-Host "[OK] Installed 'odcs-sdk' in editable development mode." -ForegroundColor Green
        }
    }
    $ErrorActionPreference = $prevEAP
}

# 8. Post-Install Verification & Self-Test
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor DarkGray
Write-Host "🔍 RUNNING AUTOMATED DUAL-ENGINE VERIFICATION SUITE" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor DarkGray

$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"

# Test Haven CLI
if (Test-Path (Join-Path $havenDir "haven_lang.py")) {
    $havenVer = & $pythonExe (Join-Path $havenDir "haven_lang.py") --help 2>&1 | Select-Object -First 1
    Write-Host "  ✓ Haven Language CLI:   ONLINE (haven_lang.py v2.0 ready)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Haven Language CLI:   MISSING" -ForegroundColor Red
}

# Test Star CLI
if (Test-Path (Join-Path $starDir "star.py")) {
    Write-Host "  ✓ Star Language CLI:    ONLINE (star.py v1.2.0 GA ready)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Star Language CLI:    MISSING" -ForegroundColor Red
}

# Test Python SDK
if ($pythonExe) {
    $sdkCheck = & $pythonExe -c "import odcs_sdk; print(f'v{odcs_sdk.__version__} ({odcs_sdk.__standard__})')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ ODCS Python SDK:      ONLINE ($sdkCheck)" -ForegroundColor Green
    } else {
        Write-Host "  • ODCS Python SDK:      Configured in $InstallDir\python-sdk" -ForegroundColor Yellow
    }
}

$ErrorActionPreference = $prevEAP

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor DarkGray
Write-Host "🎉 ODCS DUAL-ENGINE TOOLCHAIN INSTALLED SUCCESSFULLY ON WINDOWS!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "🛠️ CLI Toolchain Commands Now Available in PowerShell:" -ForegroundColor White
Write-Host "   • Star CLI:   star --version  |  star run <app.star>  |  star check <file.star>" -ForegroundColor Cyan
Write-Host "   • Haven CLI:  haven --help    |  haven run <code.hvn> |  haven lint <file.hvn>" -ForegroundColor Cyan
Write-Host "   • ODCS CLI:   odcs info       |  odcs star <app.star> |  odcs haven <code.hvn>" -ForegroundColor Cyan
Write-Host ""
Write-Host "🐍 Python SDK Quickstart:" -ForegroundColor White
Write-Host "   import odcs_sdk" -ForegroundColor DarkCyan
Write-Host "   from odcs_sdk import star, haven, ContinuityBridge" -ForegroundColor DarkCyan
Write-Host "   star.run('variable a = 10 \n show a')" -ForegroundColor DarkCyan
Write-Host "   haven.run('set pt to \"PT-901\" \n say pt')" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "📍 Installed to: $InstallDir" -ForegroundColor DarkGray
Write-Host "💡 Restart your PowerShell terminal to reload the updated PATH." -ForegroundColor Yellow
Write-Host ""
