# 🎨 LOKAAH UI Design System
## NotebookLM-Inspired Interface

---

## 🎯 Design Philosophy

**"Scholarly Modern"** - Clean, focused, intellectually stimulating

Inspired by:
- **Google NotebookLM** - Clean typography, generous whitespace
- **Notion** - Functional elegance
- **Linear** - Modern interactions
- **Duolingo** - Gamification without clutter

---

## 🌈 Color Palette

### Light Theme (Default)
```
Background:     #FAFAFA  (Warm white)
Surface:        #FFFFFF  (Pure white)
Surface Variant:#F3F4F6  (Light gray)
Border:         #E5E7EB  (Subtle gray)
Text Primary:   #111827  (Near black)
Text Secondary: #6B7280  (Gray)
Text Tertiary:  #9CA3AF  (Light gray)
```

### Dark Theme
```
Background:     #0F172A  (Slate 900)
Surface:        #1E293B  (Slate 800)
Surface Variant:#334155  (Slate 700)
Border:         #475569  (Slate 600)
Text Primary:   #F8FAFC  (Slate 50)
Text Secondary: #CBD5E1  (Slate 300)
Text Tertiary:  #94A3B8  (Slate 400)
```

### Accent Colors
```
Primary:   #7C3AED  (Violet 600) - Brand color
Success:   #10B981  (Emerald 500) - Correct answers
Warning:   #F59E0B  (Amber 500)  - Streaks
Error:     #EF4444  (Red 500)    - Wrong answers
Info:      #3B82F6  (Blue 500)   - Info/Hints
XP Gold:   #FFD700  (Gold)       - Gamification
Fire:      #FF6B35  (Orange)     - Streaks
```

---

## 🔤 Typography

**Font Family:** Inter (Google Fonts)

### Scale
| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| Display Large | 32px | Bold (700) | Hero headlines |
| Display Medium | 28px | Bold (700) | Page titles |
| Display Small | 24px | Bold (700) | Section headers |
| Headline Large | 22px | SemiBold (600) | Card titles |
| Headline Medium | 20px | SemiBold (600) | Subsection |
| Headline Small | 18px | SemiBold (600) | List headers |
| Title Large | 17px | SemiBold (600) | Item titles |
| Title Medium | 16px | SemiBold (600) | Button text |
| Title Small | 14px | SemiBold (600) | Labels |
| Body Large | 16px | Regular (400) | Paragraphs |
| Body Medium | 15px | Regular (400) | Default text |
| Body Small | 13px | Regular (400) | Captions |
| Label Large | 14px | Medium (500) | Input labels |
| Label Medium | 12px | Medium (500) | Badges |
| Label Small | 11px | Medium (500) | Tags |

---

## 🧩 Components

### 1. Glass Card
```dart
GlassCard(
  isElevated: true,
  padding: EdgeInsets.all(20),
  child: YourContent(),
)
```

**Variants:**
- `isElevated: false` - Subtle, no shadow
- `isElevated: true` - Medium shadow
- Custom `backgroundColor` - Tinted surface

### 2. Concept Chip
```dart
ConceptChip(
  label: 'Trigonometry',
  emoji: '📐',
  isSelected: true,
  onTap: () {},
)
```

**States:**
- Default - Gray background
- Selected - Purple tint + border
- Disabled - Reduced opacity

### 3. Question Card
```dart
QuestionCard(
  question: 'Find the height...',
  difficulty: 'Medium',
  marks: 3,
  tags: ['CBSE', '2025'],
  child: JSXGraphWidget(),
)
```

### 4. Message Bubble
```dart
MessageBubble(
  message: 'Let me help you...',
  isUser: false,
  avatar: VedaAvatar(),
)
```

### 5. Stat Card
```dart
StatCard(
  label: 'Streak',
  value: '7 🔥',
  subtitle: 'Days',
  icon: Icons.local_fire_department,
  color: LokaahTheme.fireOrange,
)
```

---

## 📱 Layout

### Desktop (1200px+)
```
┌────────┬───────────────────────────┬────────────┐
│        │                           │            │
│  NAV   │       MAIN CONTENT        │ RIGHT PANEL│
│ 200px  │       (flexible)          │  320px     │
│        │                           │            │
│ 📚     │  ┌─────────────────────┐  │  VEDA      │
│ 🤖     │  │                     │  │  Chat      │
│ 🏠     │  │  Question / Study   │  │            │
│ 🏆     │  │                     │  │  Stats     │
│ 👤     │  │  [Visualization]    │  │            │
│        │  │                     │  │            │
│        │  │  [Answer Input]     │  │            │
│        │  │                     │  │            │
│        │  └─────────────────────┘  │            │
│        │                           │            │
└────────┴───────────────────────────┴────────────┘
```

### Tablet (768px - 1200px)
- Collapsible side nav (70px icons only)
- Main content expanded
- Right panel as overlay/drawer

### Mobile (< 768px)
- Bottom navigation (5 tabs)
- Full-width content
- Right panel as drawer
- Floating action button for VEDA

---

## 🎭 Navigation

### Desktop Side Nav
```
┌─────────────────────┐
│  ⬜ LOKAAH          │
├─────────────────────┤
│  🏠  Home           │
│  📚  Learn          │
│  🤖  VEDA           │ ← Center highlight
│  🏆  Progress       │
│  👤  Profile        │
├─────────────────────┤
│  🌙  Dark Mode      │
└─────────────────────┘
```

### Mobile Bottom Nav
```
┌─────────────────────────────────────────┐
│  🏠    📚    ⬜🤖⬜    🏆    👤        │
│ Home  Learn   VEDA    Win    Me         │
└─────────────────────────────────────────┘
        ↑
   Elevated center button
```

---

## ✨ Micro-interactions

### Hover States
- Cards: Subtle scale (1.02) + shadow increase
- Buttons: Background darken
- Chips: Border color change

### Press States
- Scale down (0.98)
- Ripple effect (Material)

### Transitions
- Page transitions: Fade + slide (300ms)
- Card expansions: Smooth height (400ms)
- Progress bars: Ease-out cubic (500ms)

---

## 🎮 Gamification Integration

### XP Bar (Always Visible)
```
┌─────────────────────────────────────────────┐
│  ⭐ 5    ██████████████░░  240/300 XP  🔥 5 │
│       (purple gradient)     (fire streak)   │
└─────────────────────────────────────────────┘
```

### Fire Streak
- Appears in XP bar when streak >= 3
- Animated flame effect
- Orange/red gradient

### Level Up Modal
- Full-screen overlay
- Confetti animation
- Big level number
- New title unlock

---

## 📐 Spacing System

**Base Unit:** 4px

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Component internal |
| md | 16px | Default padding |
| lg | 24px | Section padding |
| xl | 32px | Large sections |
| 2xl | 48px | Hero sections |

---

## 🔲 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| sm | 6px | Small buttons, tags |
| md | 10px | Input fields |
| lg | 12px | Buttons |
| xl | 16px | Cards |
| 2xl | 20px | Large cards |
| full | 999px | Pills, avatars |

---

## 🌓 Theme Switching

```dart
// System default
MaterialApp(
  theme: LokaahTheme.lightTheme,
  darkTheme: LokaahTheme.darkTheme,
  themeMode: ThemeMode.system,
);

// Force dark
ThemeMode.dark

// Force light
ThemeMode.light
```

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 768px | Bottom nav, single column |
| Tablet | 768-1200px | Collapsible side nav |
| Desktop | > 1200px | Full 3-column layout |

---

## 🚀 Usage

### Quick Start
```dart
void main() {
  runApp(
    MaterialApp(
      theme: LokaahTheme.lightTheme,
      home: MainShell(),
    ),
  );
}
```

### Using Components
```dart
// Card
GlassCard(
  child: Text('Hello'),
)

// With elevation
GlassCard(
  isElevated: true,
  child: YourWidget(),
)

// Chip
ConceptChip(
  label: 'Algebra',
  emoji: '📊',
  isSelected: true,
)
```

---

## 🎯 Design Principles

1. **Content First** - Typography drives the design
2. **Whitespace is Premium** - Generous padding
3. **Subtle Depth** - Soft shadows, not harsh
4. **Consistent Rhythm** - 4px base unit everywhere
5. **Meaningful Motion** - Every animation has purpose

---

## 📊 Comparison: Before vs After

### Before (Generic)
- ❌ Cluttered interface
- ❌ Harsh shadows
- ❌ Small touch targets
- ❌ Boring colors
- ❌ No personality

### After (NotebookLM Style)
- ✅ Clean, airy layout
- ✅ Soft, subtle shadows
- ✅ Large, tappable areas
- ✅ Thoughtful color use
- ✅ Distinctive brand feel

---

## 🔗 Files

```
lib/
├── theme/
│   └── lokaah_theme.dart       # Theme configuration
├── widgets/ui/
│   ├── glass_card.dart         # Card components
│   └── side_navigation.dart    # Navigation
├── screens/main/
│   └── main_shell.dart         # Layout shell
└── main_notebooklm.dart        # Entry point
```

---

## 🎨 Try It

```bash
# Run the NotebookLM-style UI
flutter run -t lib/main_notebooklm.dart

# Or run design showcase
flutter run -t lib/main_notebooklm.dart -d chrome
# Then navigate to DesignShowcase
```

---

**Status:** ✅ Production Ready
**Inspired by:** Google NotebookLM
**Designed for:** CBSE Class 10 Students
**Feels:** Clean, Modern, Scholarly

---

*"Good design is as little design as possible."* - Dieter Rams
