# FCI Investigation Platform — Frontend Design Spec v2

## Design Vision

A polished, modern compliance investigation dashboard that looks like a premium SaaS product. Think: Linear, Vercel Dashboard, or Arc browser — clean, purposeful, with subtle depth and smooth motion. This is a tool investigators spend hours in, so it must be visually comfortable, fast-feeling, and impressive in demos.

**Light and dark modes** with system preference detection and manual toggle.

---

## 1. Theme System (Light/Dark Mode)

### Implementation approach
- Use Tailwind's `darkMode: 'class'` strategy in `tailwind.config.js`
- Create a `ThemeContext` (similar to AuthContext) that:
  - Reads system preference via `window.matchMedia('(prefers-color-scheme: dark)')`
  - Stores user override in `localStorage` (only theme pref — not auth data)
  - Toggles `.dark` class on `<html>` element
  - Provides `theme`, `toggleTheme`, and `isDark` to components
- Add a theme toggle button in the AppLayout header (sun/moon icon)

### Colour tokens
Extend `tailwind.config.js` with CSS custom properties so both modes share semantic names:

```
Light mode:
  --bg-primary:    #ffffff       (white)
  --bg-secondary:  #f8fafc       (slate-50)
  --bg-tertiary:   #f1f5f9       (slate-100)
  --bg-elevated:   #ffffff       (white, with shadow for depth)
  --text-primary:  #0f172a       (slate-900)
  --text-secondary:#475569       (slate-600)
  --text-muted:    #94a3b8       (slate-400)
  --border:        #e2e8f0       (slate-200)
  --border-subtle: #f1f5f9       (slate-100)

Dark mode (current, refined):
  --bg-primary:    #0f172a       (slate-900)
  --bg-secondary:  #1e293b       (slate-800)
  --bg-tertiary:   #334155       (slate-700)
  --bg-elevated:   #1e293b       (slate-800, with shadow)
  --text-primary:  #f1f5f9       (slate-100)
  --text-secondary:#94a3b8       (slate-400)
  --text-muted:    #64748b       (slate-500)
  --border:        #334155       (slate-700)
  --border-subtle: #1e293b       (slate-800)

Accent (both modes):
  --accent:        #0ea5e9       (sky-500)
  --accent-hover:  #38bdf8       (sky-400)
  --accent-muted:  #0ea5e9/10    (sky-500 at 10% opacity)
  --accent-subtle: #0ea5e9/5     (sky-500 at 5% opacity)

Status colours (both modes):
  --status-success:  #22c55e     (green-500)
  --status-warning:  #f59e0b     (amber-500)
  --status-error:    #ef4444     (red-500)
  --status-info:     #3b82f6     (blue-500)
```

All component classes should use the `dark:` prefix pattern. Example:
`bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100`

---

## 2. Typography

### Font stack
Add Inter (or Geist) as the primary font. Add to `index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

And in `tailwind.config.js`:
```js
fontFamily: {
  sans: ['Inter', 'system-ui', 'sans-serif'],
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

## 3. Global CSS & Animations

Add to `index.css` (via `@layer utilities` or plain CSS):

### Transitions (default for all interactive elements)
```css
/* Apply via Tailwind: transition-all duration-200 ease-out */
/* Or as a base layer: */
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

## 4. Component-by-Component Spec

### 4.1 AppLayout (`components/AppLayout.jsx`)

**Header bar:**
- Height: `h-14` (56px) — gives room to breathe
- Background: `bg-white/80 dark:bg-slate-900/80 glass` — frosted glass effect
- Border: `border-b border-slate-200 dark:border-slate-700/50`
- Shadow: `shadow-sm`
- Sticky: `sticky top-0 z-50`
- App title: `text-base font-semibold tracking-tight`
- Back arrow: `w-5 h-5`, wrapped in a `w-8 h-8 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center justify-center` button for a proper hit area
- Case info pills: `text-sm` with refined badge styling (see Badge spec below)
- User name: `text-sm font-medium`
- Logout: `text-sm text-slate-500 hover:text-slate-900 dark:hover:text-slate-200`
- **Theme toggle:** Sun/moon icon button, `w-8 h-8 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800`, placed next to user name
- **Animation:** Header fades in on mount: `animate-fade-in-down`

### 4.2 LoginPage (`pages/LoginPage.jsx`)

This is the first thing people see — it should feel premium.

- **Background:** Subtle gradient: `bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900`
- Optional: very subtle grid pattern or dot pattern overlay using CSS background-image
- **Card:** `max-w-md w-full bg-white dark:bg-slate-800 rounded-2xl shadow-2xl dark:shadow-none dark:border dark:border-slate-700 p-8`
- **Card top accent:** A subtle gradient bar at the top: `h-1 bg-gradient-to-r from-sky-500 to-blue-600 rounded-t-2xl` (placed above the card or as a pseudo-element)
- **App title:** `text-2xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent` — gradient text effect
- **Subtitle:** `text-sm text-slate-500 dark:text-slate-400 mt-1`
- **Input field:** `h-11 text-base rounded-xl bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-600 focus:ring-2 focus:ring-sky-500/30 focus:border-sky-500`
- **Button:** `h-11 text-base font-medium rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 active:scale-[0.98]`
- **Error message:** `animate-fade-in-up` when appearing
- **Card animation:** `animate-scale-in` on mount
- **Loading state on button:** Replace text with a small spinner, button stays the same size

### 4.3 CaseListPage (`pages/CaseListPage.jsx`)

- **Page header area:** Add a proper header section with:
  - Title: `text-2xl font-bold` — "Investigations"
  - Subtitle: `text-sm text-slate-500` — "{n} active cases" (derive from data)
  - This header should have `px-6 py-6` or similar generous spacing
- **Card grid:** Use `grid grid-cols-1 gap-4 px-6` (single column is fine for case cards)
- **Cards animate in:** Each card gets `animate-fade-in-up` with staggered delay: `style={{ animationDelay: '${index * 80}ms' }}`
- **Empty state:** If no cases, show a nice centered illustration or icon with "No cases assigned" text
- **Page animation:** Content area fades in: `animate-fade-in`

### 4.4 CaseCard (`components/cases/CaseCard.jsx`)

- **Card:** `bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 hover:border-sky-300 dark:hover:border-sky-500/50 hover:shadow-lg hover:shadow-sky-500/5 transition-all duration-200 cursor-pointer group`
- Make the **entire card** clickable (wrap in a div with onClick), not just the button
- **Case ID:** `text-lg font-semibold font-mono`
- **Badges:** See Badge spec below — `text-sm`
- **Summary:** `text-base text-slate-600 dark:text-slate-300 leading-relaxed mt-3`
- **Meta row:** `text-sm text-slate-500 dark:text-slate-400 mt-4 flex items-center gap-4`
- Add subtle icons next to meta items (user icon for subject, calendar icon for date)
- **Action button:** `px-5 py-2.5 text-sm font-medium rounded-xl` — styled like a secondary button: `border border-sky-500 text-sky-500 hover:bg-sky-50 dark:hover:bg-sky-500/10 group-hover:bg-sky-500 group-hover:text-white` (fills on card hover)
- **Card hover:** The whole card subtly lifts: `hover:-translate-y-0.5`

### 4.5 InvestigationPage — Layout (`pages/InvestigationPage.jsx`)

- **Drag handle:**
  - Outer container: `w-4 flex items-center justify-center cursor-col-resize group` (16px hit area)
  - Visible bar: `w-1 h-8 rounded-full bg-slate-300 dark:bg-slate-600 group-hover:bg-sky-500 group-hover:h-12 group-active:bg-sky-400 transition-all duration-200`
  - On hover, show a subtle glow: `group-hover:shadow-[0_0_8px_rgba(14,165,233,0.3)]`
  - Add three small dots/lines centered on the bar as a grip indicator
- **Panel transition:** When resizing, panels should NOT show text selection or jitter. The `user-select: none` is already handled during drag, but ensure `will-change: width` is set during resize for smooth rendering
- **Loading state:** Replace spinner with skeleton loading — see Skeleton Loader spec below

### 4.6 CaseHeader (`components/investigation/CaseHeader.jsx`)

- Padding: `px-6 py-5`
- Background: `bg-white dark:bg-slate-800`
- Subject ID: `text-lg font-bold font-mono`
- Badges: See Badge spec
- Summary: `text-sm text-slate-500 dark:text-slate-400 leading-relaxed mt-2`
- Bottom border: `border-b border-slate-200 dark:border-slate-700`
- **Animation:** `animate-fade-in` on mount

### 4.7 CaseDataTabs (`components/investigation/CaseDataTabs.jsx`)

- Tab text: `text-sm font-medium`
- Tab padding: `px-4 py-3`
- Container: `bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-4`
- **Active tab:** `border-b-2 border-sky-500 text-sky-600 dark:text-sky-400` — make the border `border-b-[3px]` for more presence
- **Inactive tab:** `text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-t-lg`
- **Tab transition:** Add a sliding underline indicator (animated `transform` on a pseudo-element that moves to the active tab) — OR keep it simple with just the border approach but ensure transitions are smooth
- **Animation:** Tab content panel should `animate-fade-in` when switching tabs

### 4.8 CaseDataPanel (`components/investigation/CaseDataPanel.jsx`)

- Padding: `p-6`
- Background: `bg-slate-50 dark:bg-slate-900`
- **Scroll behaviour:** Smooth scroll with `scroll-behavior: smooth`
- **Content animation:** `animate-fade-in` when tab content changes (key the wrapper on activeTab)
- Empty state: Centered, with a subtle icon and `text-sm text-slate-400`

### 4.9 MarkdownRenderer (`components/shared/MarkdownRenderer.jsx`)

- Use `prose-base` not `prose-sm`
- **Tables:**
  - Wrap in `rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700`
  - Header row: `bg-slate-100 dark:bg-slate-800 font-semibold`
  - Cells: `py-2.5 px-4 text-sm` — comfortable padding
  - Alternating rows: `even:bg-slate-50 dark:even:bg-slate-800/50`
  - Hover row: `hover:bg-slate-100 dark:hover:bg-slate-700/50`
- **Code blocks:** `rounded-lg` with slightly more padding
- **Headings:** Ensure clear visual hierarchy — `##` should be `text-lg font-semibold`, `###` should be `text-base font-semibold`
- **Light mode prose:** Override prose colours for light mode (default prose is light-friendly, prose-invert for dark)

### 4.10 ChatMessageList (`components/investigation/ChatMessageList.jsx`)

- Spacing: `space-y-5 p-5`
- Background: `bg-slate-50 dark:bg-slate-900`
- **Smooth scroll:** Use `scroll-smooth` on the container
- **Empty state:** Replace "Starting investigation..." with something nicer — a subtle icon and styled text

### 4.11 ChatMessage (`components/investigation/ChatMessage.jsx`)

**User messages:**
- Bubble: `bg-sky-50 dark:bg-sky-900/30 border border-sky-200 dark:border-sky-800/50 rounded-2xl rounded-br-md px-5 py-4`
- Text: `text-base text-slate-800 dark:text-slate-200 leading-relaxed`
- Role label: `text-sm font-semibold text-sky-700 dark:text-sky-400`
- Timestamp: `text-xs text-slate-400`
- **Animation:** `animate-fade-in-up` — appears to slide up into view
- **Image thumbnails:** `w-24 h-24 rounded-xl border-2 border-sky-200 dark:border-sky-800 hover:scale-105 transition-transform cursor-pointer` — clicking could open a lightbox (future enhancement, optional)

**Assistant messages:**
- Bubble: `bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl rounded-bl-md px-5 py-4 shadow-sm`
- Role label: `text-sm font-semibold text-slate-600 dark:text-slate-400`
- Timestamp: `text-xs text-slate-400`
- **Animation:** `animate-fade-in-up` with a slightly longer duration (0.4s)
- **Tools used footer:** `text-sm mt-3 pt-3 border-t border-slate-100 dark:border-slate-700`
  - Document titles: `text-sky-600 dark:text-sky-400 font-medium` with a small document icon before each

**Max width:** Keep `max-w-[85%]` but consider `max-w-[80%]` for cleaner look.

### 4.12 ChatInput (`components/investigation/ChatInput.jsx`)

- Container: `bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 px-5 py-4`
- **Textarea:**
  - `text-base rounded-xl bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-600`
  - `focus:ring-2 focus:ring-sky-500/30 focus:border-sky-500`
  - `rows={3}` for more comfortable input area
  - **Auto-grow:** Consider making the textarea auto-grow to fit content (up to a max of ~6 rows), then scroll. This makes typing long messages much nicer.
  - Placeholder: `text-base text-slate-400`
- **Send button:** `px-5 py-2.5 text-base font-medium rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white shadow-md shadow-sky-500/20 active:scale-[0.97] disabled:from-slate-300 disabled:to-slate-400 dark:disabled:from-slate-700 dark:disabled:to-slate-600 disabled:shadow-none`
- **Drag-over state:** `border-2 border-dashed border-sky-400 bg-sky-50/50 dark:bg-sky-900/20` with a subtle "Drop image here" overlay text
- **Image preview thumbnails:** `w-16 h-16 rounded-xl` with a nice remove button (small X in a circle, `hover:bg-red-500 hover:text-white`)

### 4.13 StreamingIndicator (`components/investigation/StreamingIndicator.jsx`)

Replace the simple bouncing dots with something more polished:

- Container: `px-5 py-3`
- **Option A (recommended):** A message-shaped container that matches assistant bubble styling but smaller, containing an animated shimmer bar:
  ```
  <div class="max-w-[200px] bg-white dark:bg-slate-800 rounded-2xl rounded-bl-md px-5 py-4 border border-slate-200 dark:border-slate-700 shadow-sm">
    <div class="flex items-center gap-3">
      <div class="flex gap-1.5">
        <!-- Three dots with stagger -->
      </div>
      <span class="text-sm text-slate-400">Thinking...</span>
    </div>
    <div class="mt-2 h-2 rounded-full animate-shimmer bg-slate-100 dark:bg-slate-700" />
  </div>
  ```
- Dots: `w-2 h-2 rounded-full bg-sky-500`
- **Animation:** The whole indicator should `animate-fade-in-up`

### 4.14 StreamingText — Blinking Cursor

When assistant messages are streaming, append a blinking cursor to the end of the content:
- In ChatMessage, if the message is currently streaming (e.g., `message.isStreaming`), append `<span class="animate-blink text-sky-500">|</span>` after the content
- Pass `isStreaming` from InvestigationPage by marking the streaming message

### 4.15 LoadingSpinner → Skeleton Loader (`components/shared/LoadingSpinner.jsx`)

Keep the spinner for button states, but add a **Skeleton** component for page/section loading:

```jsx
function Skeleton({ className }) {
  return <div className={`rounded-lg bg-slate-200 dark:bg-slate-700 animate-shimmer ${className}`} />;
}
```

Use in InvestigationPage loading state:
- Left panel: 3-4 skeleton bars of varying widths
- Right panel: 2-3 skeleton message bubbles
- This looks much more professional than a centred spinner

### 4.16 ImageUpload (`components/shared/ImageUpload.jsx`)

- Thumbnails: `w-16 h-16 rounded-xl border-2 border-slate-200 dark:border-slate-700 object-cover`
- Remove button: `absolute -top-1.5 -right-1.5 w-5 h-5 bg-slate-600 hover:bg-red-500 text-white rounded-full flex items-center justify-center text-xs transition-colors`
- **Upload button icon:** Use a proper paperclip or attachment icon, `w-9 h-9 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-sky-500`

---

## 5. Badge System

Consistent badge styling throughout (case type, status, etc.):

### Case type badges
| Type | Light | Dark |
|------|-------|------|
| Scam | `bg-red-50 text-red-700 ring-1 ring-red-200` | `bg-red-500/10 text-red-400 ring-1 ring-red-500/20` |
| CTM | `bg-amber-50 text-amber-700 ring-1 ring-amber-200` | `bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20` |
| Fraud | `bg-purple-50 text-purple-700 ring-1 ring-purple-200` | `bg-purple-500/10 text-purple-400 ring-1 ring-purple-500/20` |
| FTM | `bg-blue-50 text-blue-700 ring-1 ring-blue-200` | `bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20` |

### Status badges
| Status | Light | Dark |
|--------|-------|------|
| Open | `bg-green-50 text-green-700 ring-1 ring-green-200` | `bg-green-500/10 text-green-400 ring-1 ring-green-500/20` |
| In Progress | `bg-sky-50 text-sky-700 ring-1 ring-sky-200` | `bg-sky-500/10 text-sky-400 ring-1 ring-sky-500/20` |
| Closed | `bg-slate-100 text-slate-600 ring-1 ring-slate-200` | `bg-slate-500/10 text-slate-400 ring-1 ring-slate-500/20` |
| Escalated | `bg-red-50 text-red-700 ring-1 ring-red-200` | `bg-red-500/10 text-red-400 ring-1 ring-red-500/20` |

### Badge base
All badges: `inline-flex items-center px-2.5 py-1 rounded-full text-sm font-medium`

Update `formatters.js` to export badge colour functions that return the full class strings above, using a `dark:` prefix pattern or by accepting an `isDark` param.

---

## 6. Shadows & Depth

### Shadow scale (extend tailwind.config.js)
```js
boxShadow: {
  'soft-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 3px 0 rgba(0, 0, 0, 0.06)',
  'soft': '0 2px 8px -2px rgba(0, 0, 0, 0.08), 0 4px 12px -4px rgba(0, 0, 0, 0.05)',
  'soft-lg': '0 4px 16px -4px rgba(0, 0, 0, 0.1), 0 8px 24px -8px rgba(0, 0, 0, 0.06)',
  'soft-xl': '0 8px 32px -8px rgba(0, 0, 0, 0.12), 0 16px 48px -16px rgba(0, 0, 0, 0.08)',
  'glow-sky': '0 0 16px -4px rgba(14, 165, 233, 0.3)',
}
```

**In dark mode**, shadows are less visible, so supplement with **subtle border glows** or lighter borders on hover instead.

### Where to apply
| Element | Shadow |
|---------|--------|
| Header | `shadow-soft-sm` |
| Case cards | `shadow-soft hover:shadow-soft-lg` |
| Login card | `shadow-soft-xl` (light), `shadow-none border` (dark) |
| Chat message bubbles (assistant) | `shadow-soft-sm` |
| Buttons (primary) | `shadow-md shadow-sky-500/20` |
| Dropdowns/popovers (future) | `shadow-soft-lg` |

---

## 7. Page Transitions

For smooth route transitions, wrap the `<Routes>` in App.jsx with a simple CSS fade:

**Simple approach (no extra library):**
- Wrap page content in each page component with `<div className="animate-fade-in">...</div>`
- This gives a subtle fade-in on route change that's cheap and effective

**Better approach (optional, heavier):**
- Use `framer-motion` with `AnimatePresence` and `motion.div` for enter/exit animations
- Only add this if we want route exit animations (content fading out before new page fades in)
- For demo purposes the simple approach is likely sufficient

---

## 8. Scrollbar Styling (Both Modes)

Update `index.css` scrollbar styles for both themes:

```css
/* Light mode scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* Dark mode scrollbar */
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #475569; }
.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #64748b; }
```

---

## 9. Responsive Considerations

Not a full responsive overhaul (this is a desktop investigation tool), but:
- Minimum supported width: 1024px
- Below 1280px, the investigation panel split should default to 40/60 instead of 35/65
- Tab labels could truncate or scroll horizontally on narrow panels
- Font sizes should NOT scale down on smaller viewports — readability is paramount

---

## 10. Implementation Order

Work through in this order for maximum visual impact at each step:

1. **Theme system** — ThemeContext, tailwind dark mode config, CSS variables, toggle button. This unlocks all `dark:` classes.
2. **Global CSS** — Fonts (Inter), animations, utility classes, scrollbar styles, shadow config
3. **LoginPage** — Biggest first impression. Gradient background, polished card, animated button.
4. **AppLayout** — Header with glass effect, theme toggle, proper sizing
5. **CaseListPage + CaseCard** — Cards with hover effects, staggered animation, badges
6. **InvestigationPage layout** — Drag handle, skeleton loading
7. **CaseHeader + CaseDataTabs + CaseDataPanel** — Left panel polish
8. **ChatMessage** — Bubble styling, animations, image thumbnails
9. **ChatInput** — Rounded input, gradient send button, drag-drop state
10. **StreamingIndicator** — Shimmer bar, blinking cursor
11. **MarkdownRenderer** — Table styling, prose sizing
12. **Badge system** — Update formatters.js with full badge classes
13. **Final pass** — Check both light/dark modes, fix any inconsistencies

---

## 11. Files Changed

| File | Changes |
|------|---------|
| `tailwind.config.js` | Dark mode config, fonts, shadows, colours |
| `index.html` | Inter font link |
| `index.css` | Animations, utilities, scrollbar themes, base transitions |
| `App.jsx` | Page transition wrapper |
| **New:** `context/ThemeContext.jsx` | Theme provider, toggle, localStorage, system detection |
| `context/AuthContext.jsx` | No changes |
| `services/api.js` | No changes |
| `utils/formatters.js` | Updated badge colour functions for light/dark mode |
| `AppLayout.jsx` | Glass header, theme toggle, sizing |
| `ProtectedRoute.jsx` | No changes |
| `LoginPage.jsx` | Complete visual overhaul |
| `CaseListPage.jsx` | Page header, card animations |
| `CaseCard.jsx` | Card styling, hover effects, full-card click |
| `InvestigationPage.jsx` | Drag handle, skeleton loading, streaming cursor flag |
| `CaseHeader.jsx` | Sizing, spacing |
| `CaseDataTabs.jsx` | Tab styling, hover states |
| `CaseDataPanel.jsx` | Background, animation on tab switch |
| `ChatMessageList.jsx` | Spacing, background |
| `ChatMessage.jsx` | Bubble redesign, animations, image thumbnails, streaming cursor |
| `ChatInput.jsx` | Input styling, auto-grow, drag-drop visual |
| `StreamingIndicator.jsx` | Shimmer redesign |
| `MarkdownRenderer.jsx` | Prose sizing, table polish |
| `LoadingSpinner.jsx` | Keep spinner, add Skeleton component |
| `ImageUpload.jsx` | Thumbnail and button styling |
| **New:** `components/shared/Skeleton.jsx` | Skeleton loading component |

**One new context file, one new component. Everything else is styling updates to existing files.**
