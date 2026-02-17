# 🌐 LOKAAH Website

A **production-grade, fully responsive website** for LOKAAH - India's AI tutor for CBSE Class 10 Mathematics.

## ✨ Features

### Landing Page (`index.html`)
- 🎨 **Modern Dark Theme** - Inspired by Sarvam.ai, ChatGPT
- ✨ **Smooth Animations** - AOS scroll animations, floating orbs
- 📱 **Fully Responsive** - Desktop, tablet, mobile
- 🎯 **Sections:**
  - Hero with animated chat preview
  - Features showcase
  - How it works (4 steps)
  - Subject coverage
  - Pricing (3 tiers)
  - Testimonials
  - FAQ accordion
  - CTA + Footer

### Web App (`app.html`)
- 💬 **ChatGPT-like Interface** - Conversational AI tutor
- 📝 **Real-time Chat** - With typing indicators
- 📂 **Chat History** - Sidebar with previous conversations
- 📎 **Image Upload** - Button for Snap & Solve feature
- 📱 **Mobile Optimized** - Collapsible sidebar

---

## 🚀 Quick Start

### Option 1: Open Directly
Simply open `index.html` in your browser:
```bash
cd web_lokaah
start index.html  # Windows
open index.html     # Mac
```

### Option 2: Local Server (Recommended)
```bash
cd web_lokaah

# Python 3
python -m http.server 8000

# Node.js
npx serve

# PHP
php -S localhost:8000
```
Then visit: `http://localhost:8000`

### Option 3: VS Code Live Server
Install "Live Server" extension → Right-click `index.html` → "Open with Live Server"

---

## 📁 File Structure

```
web_lokaah/
├── index.html          # Landing page
├── app.html            # Web app (chat interface)
├── css/
│   ├── main.css        # Main styles
│   ├── animations.css  # Animations & effects
│   └── app.css         # Chat app styles
├── js/
│   ├── main.js         # Landing page scripts
│   └── app.js          # Chat app scripts
├── images/             # Images folder (empty)
└── README.md           # This file
```

---

## 🎨 Design System

### Colors
```css
--bg-primary: #0a0a0f       /* Deep black */
--bg-secondary: #12121a     /* Dark navy */
--bg-card: #16162a          /* Card background */
--accent-primary: #7c3aed   /* Violet 600 */
--accent-secondary: #a855f7 /* Violet 400 */
--text-primary: #ffffff
--text-secondary: #a0a0b0
```

### Typography
- **Font:** Inter (Google Fonts)
- **Weights:** 300, 400, 500, 600, 700

### Animations
- Scroll reveal (AOS)
- Floating gradient orbs
- Typing indicators
- Hover lift effects
- Smooth transitions

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Desktop | > 1024px | Full 2-column hero, 3-column grids |
| Tablet | 768-1024px | Single column hero, 2-column grids |
| Mobile | < 768px | Stacked layout, hamburger menu |

---

## 🔧 Customization

### Change Primary Color
Edit `css/main.css`:
```css
--accent-primary: #your-color;
--accent-secondary: #your-color;
```

### Update Content
Edit `index.html`:
- Hero title, subtitle
- Feature cards
- Pricing details
- Testimonials
- FAQ questions

### Add Images
Place images in `images/` folder and reference:
```html
<img src="images/your-image.png" alt="Description">
```

---

## 🌐 Deployment

### Netlify (Recommended)
1. Push to GitHub
2. Connect repo to Netlify
3. Build command: (leave empty)
4. Publish directory: `web_lokaah`

### Vercel
```bash
npm i -g vercel
vercel --prod
```

### GitHub Pages
1. Enable GitHub Pages in repo settings
2. Select folder: `/web_lokaah`

### Firebase Hosting
```bash
npm i -g firebase-tools
firebase init hosting
firebase deploy
```

---

## 📊 SEO Optimization

### Meta Tags Included
```html
<title>LOKAAH - AI Tutor for CBSE Class 10 Mathematics</title>
<meta name="description" content="India's first AI-powered math tutor...">
```

### Recommended Additions
1. **Favicon:** Add `favicon.ico` to root
2. **Open Graph:** For social sharing
3. **Structured Data:** Schema.org JSON-LD
4. **Analytics:** Google Analytics, Mixpanel
5. **Sitemap:** `sitemap.xml`

---

## 🎯 Conversion Optimization

### CTAs Present
- Primary: "Start Learning Free"
- Secondary: "Watch Demo"
- Pricing: "Start Free Trial"
- Sticky: Chat interface access

### Trust Signals
- "50,000+ students" social proof
- School logos (DPS, KV, etc.)
- Testimonials with photos
- FAQ addressing concerns

---

## 🔮 Future Enhancements

### Phase 2
- [ ] Blog section
- [ ] Video testimonials
- [ ] Interactive demo
- [ ] Live chat widget

### Phase 3
- [ ] User dashboard
- [ ] Progress tracking
- [ ] Payment integration
- [ ] Referral program

---

## 🐛 Browser Support

| Browser | Support |
|---------|---------|
| Chrome | ✅ Latest |
| Firefox | ✅ Latest |
| Safari | ✅ Latest |
| Edge | ✅ Latest |
| IE 11 | ❌ Not supported |

---

## 📞 Support

For questions or issues:
- Email: support@lokaah.ai
- Website: https://lokaah.ai

---

## 📄 License

© 2026 LOKAAH. All rights reserved.

---

**Built with ❤️ in India 🇮🇳**
