# FCI Investigation Platform — Frontend Design Spec v3 (Binance Dark + Gold)

## Design Vision

A premium, authoritative financial crime investigation dashboard inspired by Binance's dark-luxury aesthetic. Think Bloomberg Terminal meets modern SaaS — **dark surfaces, warm gold accents, atmospheric depth, and distinctive typography**. This is a tool investigators spend hours in, so it must be visually comfortable, fast-feeling, and impressive in demos.

**Aesthetic tone:** Professional, dark-luxury fintech. Restrained use of gold (borders, active states, primary CTAs) so it feels premium, not gaudy.

**Memorable element:** The AI streaming indicator — a gold shimmer sweep that looks like intelligence scanning through documents.

**Light and dark modes** with system preference detection and manual toggle. Dark mode is the default.

---

## 1. Theme System (Light/Dark Mode)

### Implementation approach
- Use Tailwind's `darkMode: 'class'` strategy in `tailwind.config.js`
- Create a `ThemeContext` (similar to AuthContext) that:
  - Reads system preference via `window.matchMedia('(prefers-color-scheme: dark)')`
  - Stores user override in `localStorage` (only theme pref — not auth data)
  - Toggles `.dark` or `.light` class on `<html>` element (dark is default)
  - Provides `theme`, `toggleTheme`, and `isDark` to components
- Add a theme toggle button in the AppLayout header (sun/moon icon)
- `<body>` uses `bg-surface-950 text-surface-100` (dark) / `bg-surface-50 text-surface-950` (light)

### Colour tokens — CSS Custom Properties (semantic)

```css
:root {
  /* Dark mode (default) */
  --bg-primary:     #0B0E11;
  --bg-secondary:   #12161C;
  --bg-tertiary:    #181C23;
  --bg-elevated:    #1E2329;
  --bg-surface:     #252A31;
  --text-primary:   #EAECEF;
  --text-secondary: #8B95A5;
  --text-muted:     #6A7282;
  --border:         #2E3440;
  --border-subtle:  #252A31;

  /* Gold accent */
  --accent:         #F0B90B;
  --accent-hover:   #F5C842;
  --accent-muted:   rgba(240, 185, 11, 0.15);
  --accent-subtle:  rgba(240, 185, 11, 0.07);
  --accent-glow:    rgba(240, 185, 11, 0.25);

  /* Status (same both modes) */
  --status-success: #0ECB81;   /* Binance green */
  --status-warning: #F0B90B;   /* Gold (same as accent) */
  --status-error:   #F6465D;   /* Binance red */
  --status-info:    #1E9CF4;   /* Binance blue */
}

.light {
  --bg-primary:     #F5F6F7;
  --bg-secondary:   #EAECEF;
  --bg-tertiary:    #E0E3E8;
  --bg-elevated:    #FFFFFF;
  --bg-surface:     #F5F6F7;
  --text-primary:   #12161C;
  --text-secondary: #6A7282;
  --text-muted:     #8B95A5;
  --border:         #D1D6DD;
  --border-subtle:  #EAECEF;
}
```

All component classes should use the `dark:` prefix pattern. Example:
`bg-surface-50 dark:bg-surface-800 text-surface-950 dark:text-surface-100`

---

## 2. Typography

### Font stack
**Inter is banned** — it's an overused AI aesthetic default.

**Primary font: Plus Jakarta Sans** — modern geometric sans-serif with subtle personality, excellent weight range (200–800), highly readable at all sizes.

Add to `index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

And in `tailwind.config.js`:
```js
fontFamily: {
  sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
  mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
}
```

### Size scale (apply globally)
| Element | Current | Target |
|---------|---------|--------|
| Page titles | text-sm | text-xl font-semibold |
| Section headers | text-sm | text-lg font-semibold |
| Body text / chat messages | text-sm | text-base |
| Secondary text (timestamps, meta) | text-xs | text-sm |
| Labels, badges, tab labels | text-xs | text-sm |
| Case IDs (monospace) | text-sm | text-base font-mono |
| Input fields & buttons | text-sm | text-base |
| Tiny annotations only | — | text-xs |

### Line height
Ensure body text uses `leading-relaxed` (1.625) for readability. Chat messages especially benefit from generous line height.

---

## 3. Tailwind Config — Colour Scales

### Surface scale (replaces `surface` in tailwind.config.js)

Inspired by Binance's #1E2329 dark base. Cool-neutral dark tones.

```js
surface: {
  950: '#0B0E11',   // Deepest — page background (dark mode)
  900: '#12161C',   // Main background
  850: '#181C23',   // Slightly elevated
  800: '#1E2329',   // Cards, panels (≈ Binance main dark)
  750: '#252A31',   // Elevated surfaces
  700: '#2E3440',   // Borders, dividers
  600: '#474D57',   // Muted icons, subtle text
  500: '#6A7282',   // Secondary text
  400: '#8B95A5',   // Placeholder text
  300: '#AEB7C4',   // (rarely used in dark mode)
  200: '#D1D6DD',   // (light mode secondary text)
  100: '#EAECEF',   // Primary text on dark / (light mode borders)
  50:  '#F5F6F7',   // Primary background (light mode)
}
```

### Gold accent scale (replaces `primary`)

Centered on Binance's #F0B90B.

```js
gold: {
  950: '#2D2305',
  900: '#4A3A08',
  800: '#6B540C',
  700: '#8C6E10',
  600: '#B08B14',
  500: '#F0B90B',   // ← Binance primary gold (main accent)
  400: '#F5C842',
  300: '#F8D66F',
  200: '#FBE59D',
  100: '#FDF2CE',
  50:  '#FFFBEB',
}
```

### Status colours

Use Binance's actual UI colours rather than Tailwind defaults:
- Success: `#0ECB81` (Binance green)
- Warning: `#F0B90B` (Gold, same as accent)
- Error: `#F6465D` (Binance red)
- Info: `#1E9CF4` (Binance blue)

---

## 4. Global CSS & Animations

Add to `index.css` (via `@layer utilities` or plain CSS):

### Transitions (default for all interactive elements)
```css
@layer base {
  button, a, input, textarea, [role="tab"] {
    @apply transition-all duration-200 ease-out;
  }
}
```

### Keyframe animations
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(12px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes gold-shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes pulse-subtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
```

### Utility classes
```css
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
.animate-fade-in-up { animation: fadeInUp 0.35s ease-out; }
.animate-fade-in-down { animation: fadeInDown 0.3s ease-out; }
.animate-slide-in-right { animation: slideInRight 0.3s ease-out; }
.animate-slide-in-left { animation: slideInLeft 0.3s ease-out; }
.animate-scale-in { animation: scaleIn 0.2s ease-out; }
.animate-shimmer {
  background: linear-gradient(90deg, transparent 25%, rgba(255,255,255,0.05) 50%, transparent 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.animate-gold-shimmer {
  background: linear-gradient(90deg, transparent 25%, rgba(240, 185, 11, 0.08) 50%, transparent 75%);
  background-size: 200% 100%;
  animation: gold-shimmer 2s infinite;
}
.animate-pulse-subtle { animation: pulse-subtle 2s ease-in-out infinite; }
.animate-blink { animation: blink 1s step-end infinite; }
```

### Glassmorphism utility (for elevated panels)
```css
.glass {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
```

---

## 5. Shadows & Depth

### Shadow scale (extend tailwind.config.js)

Dark backgrounds need stronger shadow values than light-optimized defaults.

```js
boxShadow: {
  'soft-sm':  '0 1px 2px rgba(0, 0, 0, 0.2), 0 1px 3px rgba(0, 0, 0, 0.15)',
  'soft':     '0 2px 8px rgba(0, 0, 0, 0.25), 0 4px 12px rgba(0, 0, 0, 0.15)',
  'soft-lg':  '0 4px 16px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(0, 0, 0, 0.18)',
  'soft-xl':  '0 8px 32px rgba(0, 0, 0, 0.35), 0 16px 48px rgba(0, 0, 0, 0.2)',
  'glow-gold': '0 0 20px -4px rgba(240, 185, 11, 0.3)',
  'glow-gold-lg': '0 0 32px -4px rgba(240, 185, 11, 0.4)',
}
```

**Light mode:** Shadows work naturally; supplement with gold glow on interactive elements.
**Dark mode:** Subtle gold border glow on hover for cards/elevated elements (more visible than box shadows on dark).

### Where to apply
| Element | Shadow |
|---------|--------|
| Header | `shadow-soft-sm` |
| Case cards | `shadow-soft hover:shadow-glow-gold` |
| Login card | `shadow-soft-xl` (light), `shadow-none border` (dark) |
| Chat message bubbles (assistant) | `shadow-soft-sm` |
| Buttons (primary) | `shadow-md shadow-gold-500/20` |
| Dropdowns/popovers (future) | `shadow-soft-lg` |

---

## 6. Backgrounds & Atmosphere

These create atmospheric depth beyond flat solid colors.

### Login page
- **Dark mode:** Radial gradient from `surface-900` center to `surface-950` edges (vignette). Overlay a very subtle dot-grid pattern at 3–5% gold opacity. Creates depth without being distracting.
- **Light mode:** Soft warm gradient from white center to `surface-100` edges. Same subtle pattern at 2% opacity.

### Investigation page panels
- **Case data panel background:** Very faint noise/grain texture (CSS-only using a tiny base64 noise PNG or SVG filter) at ~2% opacity over `surface-850`. Adds subtle depth.
- **Chat panel:** Clean solid `surface-900` (dark) / `surface-50` (light) — no texture. Chat needs max readability.

### Implementation
Grain texture as a CSS pseudo-element or background-image. Small base64 noise PNG (~1KB) tiled. Very subtle — it should feel like the surface has "material" rather than being a flat digital color.

---

## 7. Hero Moment: AI Streaming Indicator (Gold Shimmer)

This is the one thing someone will remember about the UI.

**The gold scanning shimmer.** When the AI is thinking/streaming:
- Assistant-bubble-shaped container on dark surface
- A gold shimmer sweep across the bubble (gradient moving left to right, repeating)
- Three dots pulsing in gold
- "Analyzing..." text in muted gold
- The shimmer uses the gold accent at low opacity: `linear-gradient(90deg, transparent 25%, rgba(240,185,11,0.08) 50%, transparent 75%)`
- Whole indicator fades in with `animate-fade-in-up`

This makes the AI feel like it's actively scanning through evidence — domain-appropriate, memorable, and distinctly "Binance gold."

See Section 9.13 for exact component spec.

---

## 8. Animation Choreography

### Login page (first impression — orchestrated sequence)
1. Background gradient fades in (300ms)
2. Card scales in from 0.95 (350ms, 100ms delay)
3. Title + subtitle fade in (300ms, 250ms delay)
4. Input fields fade in up (300ms, 350ms delay)
5. Button fades in up (300ms, 450ms delay)

→ Implemented via `animation-delay` CSS on each element. Total sequence: ~750ms.

### Case list page
1. Page header fades in (300ms)
2. Cards stagger in: each card `animation-delay: ${index * 100}ms` with `fadeInUp`

→ 100ms stagger between cards. Slightly more deliberate than instant.

### Investigation page load
1. Left panel slides in from left (300ms)
2. Right panel slides in from right (300ms, 100ms delay)
3. Drag handle fades in (200ms, 300ms delay)

→ Orchestrated entrance instead of everything popping in at once.

### Chat messages
- Each new message: `animate-fade-in-up`
- Streaming indicator: `animate-fade-in-up` then continuous gold shimmer

---

## 9. Component-by-Component Spec

### 9.1 AppLayout (`components/AppLayout.jsx`)

**Header bar:**
- Height: `h-14` (56px)
- Background: `bg-surface-50/80 dark:bg-surface-900/80 glass` — frosted glass effect
- Border: `border-b border-surface-200 dark:border-surface-700/50`
- Shadow: `shadow-soft-sm`
- Sticky: `sticky top-0 z-50`
- App title: `text-base font-semibold tracking-tight`
- Back arrow: `w-5 h-5`, wrapped in a `w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 flex items-center justify-center` button
- Case info pills: `text-sm` with badge styling (see Section 10)
- User name: `text-sm font-medium`
- Logout: `text-sm text-surface-500 hover:text-surface-900 dark:hover:text-surface-200`
- **Theme toggle:** Sun/moon icon button, `w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800`, placed next to user name
- **Animation:** Header fades in on mount: `animate-fade-in-down`

### 9.2 LoginPage (`pages/LoginPage.jsx`)

First impression — must feel premium.

- **Background:** Dark mode: radial gradient from `surface-900` center to `surface-950` edges + subtle dot-grid pattern at 3–5% gold opacity. Light mode: soft warm gradient from white center to `surface-100` edges + pattern at 2%.
- **Card:** `max-w-md w-full bg-surface-50 dark:bg-surface-800 rounded-2xl shadow-soft-xl dark:shadow-none dark:border dark:border-surface-700 p-8`
- **Card top accent:** `h-1 bg-gradient-to-r from-gold-600 to-gold-400 rounded-t-2xl`
- **App title:** `text-2xl font-bold bg-gradient-to-r from-gold-500 to-gold-400 bg-clip-text text-transparent` — gold gradient text
- **Subtitle:** `text-sm text-surface-500 dark:text-surface-400 mt-1`
- **Input field:** `h-11 text-base rounded-xl bg-surface-100 dark:bg-surface-900 border-surface-200 dark:border-surface-600 focus:ring-2 focus:ring-gold-500/30 focus:border-gold-500`
- **Button:** `h-11 text-base font-semibold rounded-xl bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 shadow-lg shadow-gold-500/25 hover:shadow-gold-500/40 active:scale-[0.98]` — **dark text on gold button** (Binance pattern)
- **Error message:** `animate-fade-in-up` when appearing
- **Card animation:** Orchestrated sequence per Section 8
- **Loading state on button:** Replace text with a small spinner, button stays the same size

### 9.3 CaseListPage (`pages/CaseListPage.jsx`)

- **Page header area:**
  - Title: `text-2xl font-bold` — "Investigations"
  - Subtitle: `text-sm text-surface-500` — "{n} active cases"
  - Generous spacing: `px-6 py-6`
- **Card grid:** `grid grid-cols-1 gap-4 px-6`
- **Cards animate in:** Each card gets `animate-fade-in-up` with staggered delay: `style={{ animationDelay: '${index * 100}ms' }}`
- **Empty state:** Centered icon with "No cases assigned" text
- **Page animation:** Content area fades in: `animate-fade-in`

### 9.4 CaseCard (`components/cases/CaseCard.jsx`)

- **Card:** `bg-surface-50 dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700 border-l-2 border-l-gold-500/30 p-6 hover:border-gold-300 dark:hover:border-gold-500/50 hover:shadow-glow-gold transition-all duration-200 cursor-pointer group`
- **Left accent:** `border-l-2 border-l-gold-500/30` for brand identity
- Make the **entire card** clickable (wrap in a div with onClick)
- **Case ID:** `text-lg font-semibold font-mono`
- **Badges:** See Section 10 — `text-sm`
- **Summary:** `text-base text-surface-600 dark:text-surface-300 leading-relaxed mt-3`
- **Meta row:** `text-sm text-surface-500 dark:text-surface-400 mt-4 flex items-center gap-4`
- Add subtle icons next to meta items (user icon for subject, calendar icon for date)
- **Action button:** `px-5 py-2.5 text-sm font-medium rounded-xl border border-gold-500 text-gold-500 hover:bg-gold-500 hover:text-surface-950 group-hover:bg-gold-500 group-hover:text-surface-950` — fills to gold with dark text on card hover
- **Card hover:** Subtle lift: `hover:-translate-y-0.5`

### 9.5 InvestigationPage — Layout (`pages/InvestigationPage.jsx`)

- **Drag handle:**
  - Outer container: `w-4 flex items-center justify-center cursor-col-resize group` (16px hit area)
  - Visible bar: `w-1 h-8 rounded-full bg-surface-300 dark:bg-surface-600 group-hover:bg-gold-500 group-hover:h-12 group-active:bg-gold-400 transition-all duration-200`
  - On hover, show a subtle glow: `group-hover:shadow-[0_0_8px_rgba(240,185,11,0.3)]`
  - Add three small dots/lines centered on the bar as a grip indicator
- **Panel transition:** When resizing, panels should NOT show text selection or jitter. `user-select: none` during drag, `will-change: width` for smooth rendering
- **Loading state:** Replace spinner with skeleton loading — see Skeleton Loader spec (Section 9.15)

### 9.6 CaseHeader (`components/investigation/CaseHeader.jsx`)

- Padding: `px-6 py-5`
- Background: `bg-surface-50 dark:bg-surface-800`
- Subject ID: `text-lg font-bold font-mono`
- Badges: See Section 10
- Summary: `text-sm text-surface-500 dark:text-surface-400 leading-relaxed mt-2`
- Bottom border: `border-b border-surface-200 dark:border-surface-700`
- **Animation:** `animate-fade-in` on mount

### 9.7 CaseDataTabs (`components/investigation/CaseDataTabs.jsx`)

- Tab text: `text-sm font-medium`
- Tab padding: `px-4 py-3`
- Container: `bg-surface-50 dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700 px-4`
- **Active tab:** `border-b-[3px] border-gold-500 text-gold-600 dark:text-gold-500`
- **Inactive tab:** `text-surface-500 dark:text-surface-400 hover:text-gold-400 hover:bg-surface-100 dark:hover:bg-surface-700/50 rounded-t-lg`
- **Tab transition:** Smooth border/colour transitions via `transition-all duration-200`
- **Animation:** Tab content panel should `animate-fade-in` when switching tabs

### 9.8 CaseDataPanel (`components/investigation/CaseDataPanel.jsx`)

- Padding: `p-6`
- Background: `bg-surface-100 dark:bg-surface-850` with optional faint grain texture (see Section 6)
- **Scroll behaviour:** Smooth scroll with `scroll-behavior: smooth`
- **Content animation:** `animate-fade-in` when tab content changes (key the wrapper on activeTab)
- Empty state: Centered, with a subtle icon and `text-sm text-surface-400`

### 9.9 MarkdownRenderer (`components/shared/MarkdownRenderer.jsx`)

- Use `prose-base` not `prose-sm`
- **Tables:**
  - Wrap in `rounded-lg overflow-hidden border border-surface-200 dark:border-surface-700`
  - Header row: `bg-surface-100 dark:bg-surface-800 font-semibold`
  - Cells: `py-2.5 px-4 text-sm` — comfortable padding
  - Alternating rows: `even:bg-surface-50 dark:even:bg-surface-800/50`
  - Hover row: `hover:bg-surface-100 dark:hover:bg-surface-700/50`
- **Code blocks:** `rounded-lg` with slightly more padding
- **Headings:** `##` → `text-lg font-semibold`, `###` → `text-base font-semibold`
- **Light mode prose:** Override prose colours for light mode (default prose is light-friendly, prose-invert for dark)

### 9.10 ChatMessageList (`components/investigation/ChatMessageList.jsx`)

- Spacing: `space-y-5 p-5`
- Background: `bg-surface-100 dark:bg-surface-900`
- **Smooth scroll:** `scroll-smooth` on the container
- **Empty state:** Subtle icon with styled text (not raw "Starting investigation...")

### 9.11 ChatMessage (`components/investigation/ChatMessage.jsx`)

**User messages:**
- Bubble: `bg-gold-500/10 border border-gold-500/20 rounded-2xl rounded-br-md px-5 py-4`
- Text: `text-base text-surface-800 dark:text-surface-200 leading-relaxed`
- Role label: `text-sm font-semibold text-gold-600 dark:text-gold-500`
- Timestamp: `text-xs text-surface-400`
- **Animation:** `animate-fade-in-up`
- **Image thumbnails:** `w-24 h-24 rounded-xl border-2 border-gold-200 dark:border-gold-800 hover:scale-105 transition-transform cursor-pointer`

**Assistant messages:**
- Bubble: `bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-2xl rounded-bl-md px-5 py-4 shadow-soft-sm`
- Role label: `text-sm font-semibold text-surface-600 dark:text-surface-400`
- Timestamp: `text-xs text-surface-400`
- **Animation:** `animate-fade-in-up` with slightly longer duration (0.4s)
- **Tools used footer:** `text-sm mt-3 pt-3 border-t border-surface-100 dark:border-surface-700`
  - Document titles: `text-gold-600 dark:text-gold-400 font-medium` with a small document icon

**Streaming cursor:**
- When message is streaming, append `<span class="animate-blink text-gold-500">▎</span>` after content

**Max width:** `max-w-[80%]`

### 9.12 ChatInput (`components/investigation/ChatInput.jsx`)

- Container: `bg-surface-50 dark:bg-surface-800 border-t border-surface-200 dark:border-surface-700 px-5 py-4`
- **Textarea:**
  - `text-base rounded-xl bg-surface-100 dark:bg-surface-900 border-surface-200 dark:border-surface-600`
  - `focus:ring-2 focus:ring-gold-500/30 focus:border-gold-500`
  - `rows={3}`, auto-grow up to ~6 rows then scroll
  - Placeholder: `text-base text-surface-400`
- **Send button:** `px-5 py-2.5 text-base font-medium rounded-xl bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 shadow-md shadow-gold-500/20 active:scale-[0.97] disabled:from-surface-300 disabled:to-surface-400 dark:disabled:from-surface-700 dark:disabled:to-surface-600 disabled:shadow-none`
- **Drag-over state:** `border-2 border-dashed border-gold-400 bg-gold-500/5` with "Drop image here" overlay
- **Image preview thumbnails:** `w-16 h-16 rounded-xl` with remove button (`hover:bg-red-500 hover:text-white`)

### 9.13 StreamingIndicator (`components/investigation/StreamingIndicator.jsx`)

Major redesign — the "hero moment" of the UI.

```
<div class="max-w-[200px] bg-surface-50 dark:bg-surface-800 rounded-2xl rounded-bl-md px-5 py-4 border border-surface-200 dark:border-surface-700 shadow-soft-sm animate-fade-in-up relative overflow-hidden">
  <!-- Gold shimmer overlay -->
  <div class="absolute inset-0 animate-gold-shimmer pointer-events-none" />

  <div class="relative flex items-center gap-3">
    <div class="flex gap-1.5">
      <!-- Three dots pulsing in gold -->
      <div class="w-2 h-2 rounded-full bg-gold-500 animate-pulse-subtle" style="animation-delay: 0ms" />
      <div class="w-2 h-2 rounded-full bg-gold-500 animate-pulse-subtle" style="animation-delay: 200ms" />
      <div class="w-2 h-2 rounded-full bg-gold-500 animate-pulse-subtle" style="animation-delay: 400ms" />
    </div>
    <span class="text-sm text-gold-500/70">Analyzing...</span>
  </div>
</div>
```

### 9.14 ImageUpload (`components/shared/ImageUpload.jsx`)

- Thumbnails: `w-16 h-16 rounded-xl border-2 border-surface-200 dark:border-surface-700 object-cover`
- Remove button: `absolute -top-1.5 -right-1.5 w-5 h-5 bg-surface-600 hover:bg-red-500 text-white rounded-full flex items-center justify-center text-xs transition-colors`
- **Upload button icon:** Paperclip/attachment icon, `w-9 h-9 rounded-xl hover:bg-surface-100 dark:hover:bg-surface-700 flex items-center justify-center text-surface-400 hover:text-gold-500`

### 9.15 Skeleton Loader (`components/shared/Skeleton.jsx`)

**New component.** Keep the existing spinner for button states, but use skeletons for page/section loading.

```jsx
function Skeleton({ className }) {
  return <div className={`rounded-lg bg-surface-200 dark:bg-surface-700 animate-shimmer ${className}`} />;
}
```

Use in InvestigationPage loading state:
- Left panel: 3–4 skeleton bars of varying widths
- Right panel: 2–3 skeleton message bubbles

---

## 10. Badge System

Consistent badge styling throughout (case type, status).

### Badge base
All badges: `inline-flex items-center px-2.5 py-1 rounded-full text-sm font-medium`

### Case type badges
| Type | Dark Mode | Light Mode |
|------|-----------|------------|
| Scam | `bg-red-500/10 text-red-400 ring-1 ring-red-500/20` | `bg-red-50 text-red-700 ring-1 ring-red-200` |
| CTM | `bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20` | `bg-amber-50 text-amber-700 ring-1 ring-amber-200` |
| Fraud | `bg-purple-500/10 text-purple-400 ring-1 ring-purple-500/20` | `bg-purple-50 text-purple-700 ring-1 ring-purple-200` |
| FTM | `bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20` | `bg-blue-50 text-blue-700 ring-1 ring-blue-200` |

### Status badges
| Status | Dark Mode | Light Mode |
|--------|-----------|------------|
| Open | `bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20` | `bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200` |
| In Progress | `bg-gold-500/10 text-gold-500 ring-1 ring-gold-500/20` | `bg-gold-50 text-gold-700 ring-1 ring-gold-200` |
| Closed | `bg-surface-500/10 text-surface-400 ring-1 ring-surface-500/20` | `bg-surface-100 text-surface-600 ring-1 ring-surface-200` |
| Escalated | `bg-red-500/10 text-red-400 ring-1 ring-red-500/20` | `bg-red-50 text-red-700 ring-1 ring-red-200` |

**Note:** "In Progress" uses gold (the brand accent) instead of generic sky. Open uses emerald (#0ECB81 Binance green).

Update `formatters.js` to export badge colour functions that return the full class strings above, using a `dark:` prefix pattern or by accepting an `isDark` param.

---

## 11. Scrollbar Styling (Both Modes)

```css
/* Light mode scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #AEB7C4; border-radius: 3px; } /* surface-300 */
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #8B95A5; } /* surface-400 */

/* Dark mode scrollbar */
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #474D57; } /* surface-600 */
.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #6A7282; } /* surface-500, visible on hover */
```

---

## 12. Page Transitions

Wrap page content in each page component with `<div className="animate-fade-in">...</div>` for a subtle fade-in on route change.

**Optional heavier approach:** `framer-motion` with `AnimatePresence` — only if exit animations are needed. Simple approach is sufficient for demo.

---

## 13. Responsive Considerations

Desktop investigation tool — not a full responsive overhaul:
- Minimum supported width: 1024px
- Below 1280px, investigation panel split defaults to 40/60 instead of 35/65
- Tab labels could truncate or scroll horizontally on narrow panels
- Font sizes should NOT scale down on smaller viewports — readability is paramount

---

## 14. Implementation Order

Work through in this order for maximum visual impact at each step:

1. **Theme system** — ThemeContext, tailwind dark mode config, CSS variables, toggle button, surface + gold colour scales
2. **Global CSS** — Plus Jakarta Sans font, animations, utility classes, scrollbar styles, shadow config
3. **LoginPage** — Biggest first impression. Radial gradient + dot-grid background, gold gradient card, orchestrated animation
4. **AppLayout** — Header with glass effect, theme toggle, proper sizing
5. **CaseListPage + CaseCard** — Gold-accented cards with hover glow, staggered animation, badges
6. **InvestigationPage layout** — Gold drag handle, skeleton loading, panel slide-in
7. **CaseHeader + CaseDataTabs + CaseDataPanel** — Left panel polish with gold active tabs, grain texture
8. **ChatMessage** — Gold-tinted user bubbles, animations, image thumbnails, streaming cursor
9. **ChatInput** — Rounded input, gold gradient send button, drag-drop state
10. **StreamingIndicator** — Gold shimmer sweep hero moment
11. **MarkdownRenderer** — Table styling, prose sizing
12. **Badge system** — Update formatters.js with full badge classes (gold "In Progress", Binance status colours)
13. **Final pass** — Check both light/dark modes, verify colour consistency, test all animations

---

## 15. Files Changed

| File | Changes |
|------|---------|
| `tailwind.config.js` | Dark mode config, Plus Jakarta Sans font, gold + surface colour scales, shadows |
| `index.html` | Plus Jakarta Sans + JetBrains Mono font links |
| `index.css` | Animations (incl. gold-shimmer), utilities, scrollbar themes, base transitions, grain texture, CSS custom properties |
| `App.jsx` | Page transition wrapper |
| **New:** `context/ThemeContext.jsx` | Theme provider, toggle, localStorage, system detection (dark default) |
| `context/AuthContext.jsx` | No changes |
| `services/api.js` | No changes |
| `utils/formatters.js` | Updated badge colour functions for light/dark mode with gold + Binance colours |
| `AppLayout.jsx` | Glass header, theme toggle, surface colour classes |
| `ProtectedRoute.jsx` | No changes |
| `LoginPage.jsx` | Complete visual overhaul — radial gradient bg, gold accents, orchestrated animation |
| `CaseListPage.jsx` | Page header, staggered card animations |
| `CaseCard.jsx` | Gold hover glow, gold left accent, gold action button, full-card click |
| `InvestigationPage.jsx` | Gold drag handle, skeleton loading, streaming cursor flag, panel slide-in |
| `CaseHeader.jsx` | Surface colour classes, sizing |
| `CaseDataTabs.jsx` | Gold active tab underline, gold hover |
| `CaseDataPanel.jsx` | Surface-850 background, grain texture, animation on tab switch |
| `ChatMessageList.jsx` | Surface background, spacing |
| `ChatMessage.jsx` | Gold user bubbles, gold streaming cursor, animations, thumbnails |
| `ChatInput.jsx` | Gold gradient send button, gold focus ring, drag-drop visual |
| `StreamingIndicator.jsx` | Gold shimmer sweep redesign (hero moment) |
| `MarkdownRenderer.jsx` | Prose sizing, table polish with surface colours |
| `LoadingSpinner.jsx` | Keep spinner for buttons |
| `ImageUpload.jsx` | Thumbnail and button styling with gold hover |
| **New:** `components/shared/Skeleton.jsx` | Skeleton loading component with surface colours |

**One new context file, one new component. Everything else is styling updates to existing files.**
