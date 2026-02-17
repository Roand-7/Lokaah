# 🎬 Installing FFmpeg on Windows (No Admin Required)

## Quick Installation Guide

FFmpeg is needed only for Manim math animations. The rest of LOKAAH works without it.

---

## Method 1: Manual Download (Recommended - No Admin)

### Step 1: Download FFmpeg

1. Visit: **https://www.gyan.dev/ffmpeg/builds/**
2. Download: **ffmpeg-release-essentials.zip** (~70MB)
3. Or direct link: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

### Step 2: Extract Files

1. Extract the ZIP file to: `C:\Users\Lenovo\ffmpeg`
2. After extraction, you should see: `C:\Users\Lenovo\ffmpeg\ffmpeg-7.x-essentials_build\bin\ffmpeg.exe`

### Step 3: Add to PATH (Temporary)

In PowerShell (current session only):

```powershell
# Navigate to your project
cd C:\Users\Lenovo\lokaah_app

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Add ffmpeg to PATH for this session
$ffmpegPath = "C:\Users\Lenovo\ffmpeg\ffmpeg-7.1-essentials_build\bin"
$env:Path += ";$ffmpegPath"

# Verify installation
ffmpeg -version
```

### Step 4: Add to PATH (Permanent) - Optional

**Windows 10/11:**

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** tab → **Environment Variables**
3. Under **User variables**, find `Path` → **Edit**
4. Click **New** → Add: `C:\Users\Lenovo\ffmpeg\ffmpeg-7.1-essentials_build\bin`
5. Click **OK** on all dialogs
6. **Restart PowerShell** for changes to take effect

**Or use PowerShell (permanent, but requires new terminal):**

```powershell
# Get current user PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Add ffmpeg
$newPath = $currentPath + ";C:\Users\Lenovo\ffmpeg\ffmpeg-7.1-essentials_build\bin"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# Restart PowerShell to take effect
```

---

## Method 2: Chocolatey with Admin Rights

If you can run PowerShell as Administrator:

```powershell
# Right-click PowerShell → Run as Administrator
choco install ffmpeg -y
```

---

## Method 3: Winget (Windows 11)

If you have Windows Package Manager:

```powershell
winget install ffmpeg
```

---

## Verify Installation

After any method, verify with:

```powershell
ffmpeg -version
```

Expected output:
```
ffmpeg version 7.x Copyright (c) 2000-2024 the FFmpeg developers
built with gcc 14.x ...
```

---

## Troubleshooting

### "ffmpeg is not recognized as an internal or external command"

**Solution:** PATH not set correctly. Run this in your PowerShell:

```powershell
# Find where ffmpeg.exe is located
Get-ChildItem -Path "C:\Users\Lenovo\ffmpeg" -Filter "ffmpeg.exe" -Recurse

# Copy the path shown (e.g., C:\Users\Lenovo\ffmpeg\ffmpeg-7.1-essentials_build\bin)
# Then add to PATH:
$env:Path += ";C:\Users\Lenovo\ffmpeg\ffmpeg-7.1-essentials_build\bin"
```

### "Access is denied" errors with Chocolatey

**Solution:** Run PowerShell as Administrator (right-click → Run as Administrator)

### Want to skip ffmpeg installation?

**LOKAAH works fine without ffmpeg!** You just won't have Manim animations. All other features (VEDA, ORACLE, PULSE, ATLAS, Photo Solver, JSXGraph) work perfectly.

To disable Manim in the app:

```python
# In app/services/manim_generator.py, the code already handles missing ffmpeg gracefully
# No changes needed - animations will simply return an error message to users
```

---

## Testing FFmpeg with LOKAAH

Once installed, test Manim animations:

```powershell
# Activate virtual environment
cd C:\Users\Lenovo\lokaah_app
& .\.venv\Scripts\Activate.ps1

# Install Manim
pip install manim

# Start server
python main.py

# In another terminal, test animation endpoint:
curl -X POST "http://localhost:8000/api/v1/animation/generate?concept=quadratic_formula&quality=medium_quality"
```

---

## Quick Setup Commands (Copy-Paste)

```powershell
# 1. Download manually from https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
# 2. Extract to C:\Users\Lenovo\ffmpeg
# 3. Run these:

cd C:\Users\Lenovo\lokaah_app
& .\.venv\Scripts\Activate.ps1
$env:Path += ";C:\Users\Lenovo\ffmpeg\ffmpeg-7.1-essentials_build\bin"
ffmpeg -version
pip install manim
python main.py
```

---

**Status:** ✅ Ready to use LOKAAH with or without ffmpeg!
