# Frontend Design Overhaul — Status Report

**Date:** 2026-03-04
**Spec:** `client/DESIGN_SPEC.md` (v3 — Binance Dark + Gold)
**Status:** Complete (all 13 steps implemented), with post-implementation refinements applied

---

## What Was Done

### All 13 Implementation Steps Completed

Following the order in Section 14 of `DESIGN_SPEC.md`:

1. **Theme system** — Created `ThemeContext.jsx` with system preference detection, localStorage persistence, `useLayoutEffect` for synchronous class toggling. Inline `<script>` in `index.html` prevents flash of wrong theme. Tailwind `darkMode: 'class'` configured.

2. **Global CSS** — Plus Jakarta Sans + JetBrains Mono fonts loaded via Google Fonts. 10 keyframe animations (fadeIn, fadeInUp, fadeInDown, slideInRight, slideInLeft, scaleIn, shimmer, gold-shimmer, pulse-subtle, blink). Utility classes, glassmorphism, grain texture, base transitions, scrollbar theming for both modes. CSS custom properties for semantic colour tokens.

3. **LoginPage** — Radial gradient + gold dot-grid background. Gold gradient title text. Orchestrated 5-stage animation sequence (staggered delays). Gold gradient button with inline spinner loading state.

4. **AppLayout** — Frosted glass header (`backdrop-filter: blur(12px)` + 80% opacity background). Sun/moon theme toggle button. Gold hover accents. `animate-fade-in-down` entrance.

5. **CaseListPage + CaseCard** — "Investigations" header with case count. Staggered `animate-fade-in-up` per card. Gold left accent border, `hover:shadow-glow-gold`, `hover:-translate-y-0.5` lift. Full-card click. Gold outline button that fills on hover. Meta row with user/calendar icons.

6. **InvestigationPage layout** — Gold drag handle with grip dots and `hover:shadow-glow-gold` glow. Skeleton loading state (`Skeleton.jsx` created). Panel slide-in animations (left/right). `isStreaming` flag on messages for cursor display.

7. **CaseHeader + CaseDataTabs + CaseDataPanel** — Gold active tab underline (`border-gold-500`). Gold hover on inactive tabs. Grain texture background on case data panel. `animate-fade-in` on tab content switch.

8. **ChatMessage** — Gold-tinted user bubbles (`bg-gold-500/10`). AI messages fill full container width (no max-width). User messages capped at `max-w-[75%]`, right-aligned. Gold blinking streaming cursor. Gold document references in tools footer. `animate-fade-in-up` on all messages.

9. **ChatInput** — ChatGPT-style unified input: textarea fills full width with `rounded-2xl` container. Attach (paperclip) button overlaid bottom-left, send arrow button overlaid bottom-right. Image thumbnails appear above input. `focus-within:ring-gold-500/30` glow. Drag-drop state with gold ring.

10. **StreamingIndicator** — Gold shimmer sweep hero moment. Three pulsing gold dots + "Analyzing..." text. `animate-gold-shimmer` overlay. `animate-fade-in-up` entrance.

11. **MarkdownRenderer** — `prose-base` (up from `prose-sm`). Custom table components with rounded borders, surface-coloured headers, hover rows. Heading size scale (h2 → `text-lg`, h3 → `text-base`). Inline code styling.

12. **Badge system** — Ring-based badges in `formatters.js`. Gold for "In Progress", emerald for "Open", red for "Escalated". Case type badges: red (scam), amber (ctm), blue (ftm), purple (fraud). Full `dark:` prefix support.

13. **Final pass** — Build verification, react-markdown v9 compatibility fix for code components.

### Post-Implementation Refinements

After the initial 13-step implementation, the following issues were identified and fixed during user testing:

- **Theme toggle not working:** Root cause was `useEffect` (async, after paint) + stale localStorage from system preference detection. Fixed by switching to `useLayoutEffect` and adding an inline `<script>` in `index.html` that applies the theme class before CSS loads. Vite cache (`node_modules/.vite`) must be cleared when `tailwind.config.js` changes.

- **Chat messages too spread out:** Messages stretched to fill the full right panel width. User and AI messages were far apart. Fixed by adding a centered container. AI messages now fill full container width; user messages are `max-w-[75%]` right-aligned — standard chat UX.

- **Chat input misaligned:** Attach button, textarea, and send button were side-by-side, making the input narrower than the chat. Redesigned to ChatGPT-style: textarea fills container width, buttons overlaid inside it.

- **Chat container fixed width:** `max-w-5xl` didn't scale with the panel. Replaced with percentage-based padding (`paddingLeft: '5%', paddingRight: '5%'` as inline styles) so the chat area grows/shrinks fluidly with the drag divider.

- **Dark mode too dark:** `surface-950` (`#0B0E11`) page background felt too jet-black. Bumped dark mode backgrounds up one step: page bg is now `surface-900` (`#12161C`), chat area is `surface-850` (`#181C23`). CSS custom properties updated to match.

---

## Files Changed (from original codebase)

### New Files (2)
| File | Purpose |
|------|---------|
| `src/context/ThemeContext.jsx` | Theme provider with system detection, localStorage, toggle |
| `src/components/shared/Skeleton.jsx` | Shimmer skeleton loader for loading states |

### Modified Files (20)
| File | Key Changes |
|------|-------------|
| `tailwind.config.js` | `darkMode: 'class'`, Plus Jakarta Sans/JetBrains Mono fonts, Binance surface + gold colour scales, dark-optimized shadow system |
| `index.html` | Google Fonts links, inline theme script, light/dark body classes |
| `src/index.css` | CSS custom properties, keyframe animations, utility classes, scrollbar theming, glassmorphism, grain texture, base transitions, prose overrides |
| `src/main.jsx` | Wrapped app in `ThemeProvider` |
| `src/components/AppLayout.jsx` | Glass header, theme toggle, gold hover, surface-900 dark bg |
| `src/pages/LoginPage.jsx` | Radial gradient bg, gold gradient card, orchestrated animation |
| `src/pages/CaseListPage.jsx` | Page header with count, staggered cards, empty state |
| `src/pages/InvestigationPage.jsx` | Gold drag handle, skeleton loading, panel slide-in, isStreaming flag |
| `src/components/cases/CaseCard.jsx` | Gold accents, hover glow, full-card click, meta icons |
| `src/components/investigation/CaseHeader.jsx` | Larger title, badge system, animation |
| `src/components/investigation/CaseDataTabs.jsx` | Gold active tab, gold hover |
| `src/components/investigation/CaseDataPanel.jsx` | Grain texture, tab-switch animation, empty state icon |
| `src/components/investigation/ChatMessageList.jsx` | Percentage-based padding, surface-850 dark bg |
| `src/components/investigation/ChatMessage.jsx` | Gold user bubbles, full-width AI messages, streaming cursor, gold tool refs |
| `src/components/investigation/ChatInput.jsx` | ChatGPT-style overlay input, percentage-based padding |
| `src/components/investigation/StreamingIndicator.jsx` | Gold shimmer hero moment, percentage-based padding |
| `src/components/shared/MarkdownRenderer.jsx` | prose-base, custom table/heading/code components |
| `src/components/shared/LoadingSpinner.jsx` | Gold spinner accent |
| `src/components/shared/ImageUpload.jsx` | showButton/showThumbnails props, gold hover, sized thumbnails |
| `src/utils/formatters.js` | Ring-based badge system with gold/emerald/Binance colours |

---

## Uncommitted Changes

There are 6 files with uncommitted changes (the dark mode lightening + other recent refinements). These should be committed:

```
modified: client/index.html
modified: client/src/components/AppLayout.jsx
modified: client/src/components/investigation/ChatInput.jsx
modified: client/src/components/investigation/ChatMessageList.jsx
modified: client/src/components/shared/MarkdownRenderer.jsx
modified: client/src/index.css
```

---

## Known Considerations for Next Session

- **Vite cache:** After changing `tailwind.config.js`, always clear `node_modules/.vite` and restart the dev server
- **localStorage theme:** The theme preference is stored in `fci-theme` localStorage key. If the toggle seems broken, clearing this value is the first debug step
- **Tailwind arbitrary values:** Some Tailwind JIT classes (e.g. `w-[90%]`) may not generate without a dev server restart. For critical layout, inline styles are more reliable (as used for chat padding)
- **Light mode:** Fully supported and toggleable. All components use `dark:` prefix pattern. Light mode has not been extensively tested beyond basic verification — may need a polish pass
- **The design spec (`DESIGN_SPEC.md`)** is now fully implemented. Any further design work is refinement beyond the spec
