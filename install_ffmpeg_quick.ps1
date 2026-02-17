# Quick FFmpeg Installation Script (No Admin Required)
# Run this in PowerShell: .\install_ffmpeg_quick.ps1

Write-Host "=== FFmpeg Quick Install ===" -ForegroundColor Cyan
Write-Host "This will download and install ffmpeg to your home directory.`n" -ForegroundColor White

# 1. Download ffmpeg
Write-Host "[1/4] Downloading ffmpeg (~70MB)..." -ForegroundColor Green
$url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$output = "$HOME\Downloads\ffmpeg.zip"

try {
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    Write-Host "      ✅ Downloaded successfully" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Download failed: $_" -ForegroundColor Red
    exit 1
}

# 2. Extract
Write-Host "`n[2/4] Extracting files..." -ForegroundColor Green
try {
    Expand-Archive -Path $output -DestinationPath "$HOME\ffmpeg" -Force
    Write-Host "      ✅ Extracted successfully" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Extraction failed: $_" -ForegroundColor Red
    exit 1
}

# 3. Find ffmpeg.exe
Write-Host "`n[3/4] Locating ffmpeg.exe..." -ForegroundColor Green
$ffmpegExe = Get-ChildItem -Path "$HOME\ffmpeg" -Filter "ffmpeg.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1

if ($ffmpegExe) {
    $ffmpegBin = $ffmpegExe.DirectoryName
    Write-Host "      ✅ Found at: $ffmpegBin" -ForegroundColor Green
} else {
    Write-Host "      ❌ Could not find ffmpeg.exe" -ForegroundColor Red
    exit 1
}

# 4. Add to PATH (current session)
Write-Host "`n[4/4] Adding to PATH..." -ForegroundColor Green
$env:Path += ";$ffmpegBin"
Write-Host "      ✅ Added to PATH (current session)" -ForegroundColor Green

# 5. Test
Write-Host "`n=== Testing Installation ===" -ForegroundColor Cyan
try {
    $version = & ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host $version -ForegroundColor White
    Write-Host "`n✅ SUCCESS! ffmpeg is now available in this PowerShell session." -ForegroundColor Green
} catch {
    Write-Host "❌ Test failed: $_" -ForegroundColor Red
    exit 1
}

# 6. Instructions for permanent PATH
Write-Host "`n=== To Make Permanent ===" -ForegroundColor Yellow
Write-Host "To use ffmpeg in NEW PowerShell windows, add to PATH permanently:" -ForegroundColor White
Write-Host "`n1. Press Win+R, type: sysdm.cpl" -ForegroundColor Cyan
Write-Host "2. Advanced → Environment Variables" -ForegroundColor Cyan
Write-Host "3. Under 'User variables', select Path → Edit" -ForegroundColor Cyan
Write-Host "4. Click New → Paste: $ffmpegBin" -ForegroundColor Cyan
Write-Host "5. Click OK on all dialogs`n" -ForegroundColor Cyan

Write-Host "OR run this command (requires restarting PowerShell after):" -ForegroundColor White
Write-Host '[Environment]::SetEnvironmentVariable("Path", $env:Path + ";' + $ffmpegBin + '", "User")' -ForegroundColor Green

Write-Host "`n=== For THIS Session ===" -ForegroundColor Yellow
Write-Host "ffmpeg is already available! You can now run:" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor Cyan
Write-Host "  pip install manim" -ForegroundColor Cyan
Write-Host "`nEnjoy! 🚀" -ForegroundColor Green
