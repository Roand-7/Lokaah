# LOKAAH - Required Assets

## Missing Image Assets

The following image assets need to be created for the website to be fully production-ready:

### 1. Favicon (URGENT)
**Path:** `web_lokaah/images/favicon.ico`
**Dimensions:** 16x16, 32x32, 48x48 (multi-size ICO file)
**Design:** 
- Background: Deep Royal Blue (#0F172A)
- Letter "L" in Saffron (#FF9933)
- Font: Montserrat, bold/extrabold
- Optional: Rounded corners (6px radius)

**Temporary Solution:** A simple SVG favicon has been created at `images/favicon.svg`

### 2. Open Graph Image (for Social Sharing)
**Path:** `web_lokaah/images/og-image.png`
**Dimensions:** 1200x630px (Facebook/LinkedIn) or 1200x627px (Twitter)
**Design:**
- Background: Gradient from Deep Royal Blue to darker shade
- Main text: "LOKAAH" in Montserrat (large, bold)
- Subtitle: "Learn Smarter, Not Harder" in Inter
- Accent: Saffron color (#FF9933) for highlights
- Optional: Simple geometric shapes or learning-related icons

### 3. Additional Recommended Assets

#### Logo Variations
- `images/logo-light.svg` - For dark backgrounds
- `images/logo-dark.svg` - For light backgrounds  
- `images/logo-icon.svg` - Just the "L" icon

#### Feature Section Graphics
- `images/feature-adaptive.svg` - Illustration for adaptive learning
- `images/feature-visual.svg` - Illustration for visual explanations
- `images/feature-progress.svg` - Illustration for progress tracking

## Current Status

✅ SVG Favicon created (temporary)
❌ ICO Favicon needed for better browser support
❌ OG Image needed for social media sharing
⚠️  Feature illustrations (optional but recommended)

## Tools to Create These Assets

### Free Options:
1. **Favicon Generator:** https://realfavicongenerator.net/
   - Upload your SVG and generate multi-size ICO
2. **Canva:** https://canva.com
   - Create OG image with templates
3. **Figma:** https://figma.com
   - Design all assets (free tier available)

### Quick CLI Options:
```bash
# Convert SVG to ICO (requires ImageMagick)
magick convert favicon.svg -define icon:auto-resize=16,32,48 favicon.ico

# Create OG image placeholder (requires ImageMagick)
magick -size 1200x630 xc:#0F172A -font Montserrat-Bold -pointsize 72 -fill #FF9933 \
  -gravity center -annotate +0-50 'LOKAAH' \
  -font Inter-Regular -pointsize 36 -fill white \
  -gravity center -annotate +0+50 'Learn Smarter, Not Harder' \
  og-image.png
```

## Temporary HTML Fix

The HTML currently references these images. If you want to deploy immediately:

1. Update index.html to use the SVG favicon:
   ```html
   <link rel="icon" href="images/favicon.svg" type="image/svg+xml">
   ```

2. Remove or comment out OG image tags until images are ready:
   ```html
   <!-- <meta property="og:image" content="images/og-image.png"> -->
   <!-- <meta name="twitter:image" content="images/og-image.png"> -->
   ```

## Priority

**HIGH:** Favicon (affects browser tabs and bookmarks)
**MEDIUM:** OG Image (affects social media sharing)
**LOW:** Feature illustrations (nice to have, doesn't break functionality)
