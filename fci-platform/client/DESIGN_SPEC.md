# FCI Investigation Platform — Frontend Design Spec

## Overview

The frontend is functionally complete but visually raw. This spec defines the styling overhaul needed to make it feel like a polished, professional compliance investigation tool. **No structural/logic changes** — this is purely visual.

The app is built with React 18, Tailwind CSS 3, and uses a custom dark theme with `primary` (blue) and `surface` (slate) color scales defined in `tailwind.config.js`.

---

## Global Typography & Spacing

**Problem:** Almost everything uses `text-xs` or `text-sm`, making the entire UI feel cramped and hard to scan.

### Base sizes to apply:
- **Body text / chat messages / case data content:** `text-base` (16px)
- **Secondary text (timestamps, metadata):** `text-sm` (14px)
- **Labels, badges, tab labels:** `text-sm` (14px) — currently `text-xs`, bump up one step
- **Headers (case ID, page titles):** `text-lg` or `text-xl`
- **Page header (AppLayout):** `text-base` for app title
- **Chat role labels ("You" / "AI Assistant"):** `text-sm` with `font-semibold`

### Spacing:
- Increase `px-4 py-3` to `px-6 py-4` on major containers (header, chat input, case header)
- Chat messages: increase `space-y-4` to `space-y-5` or `space-y-6` in ChatMessageList
- Case data panel padding: `p-4` → `p-6`
- Give breathing room between badge clusters and text content

---

## Component-by-Component Spec

### 1. AppLayout (`components/AppLayout.jsx`)
- App title: bump to `text-base font-semibold`, keep the clickable Link to /cases
- Back arrow: increase SVG from `w-4 h-4` to `w-5 h-5`
- Header bar: increase vertical padding to `py-3`
- User name: `text-sm`
- Logout button: `text-sm` (currently `text-xs`)
- Add subtle bottom shadow: `shadow-md` or `shadow-lg` on the header for depth

### 2. LoginPage (`pages/LoginPage.jsx`)
- Title: `text-2xl font-bold`
- Subtitle: `text-sm` is fine
- Input field: increase height with `py-2.5`, `text-base`
- Button: `py-2.5 text-base`
- Card: add subtle shadow `shadow-xl`, maybe increase max-width slightly to `max-w-md`
- Add a subtle accent — e.g., a thin `border-t-2 border-primary-500` on the card top

### 3. CaseListPage (`pages/CaseListPage.jsx`)
- Page title "Investigation Cases": add one if missing, or ensure the header area has a clear title
- Add a brief subtitle or case count ("3 open cases")
- Increase gap between case cards

### 4. CaseCard (`components/cases/CaseCard.jsx`)
- Case ID: `text-base font-mono font-semibold`
- Badges: `text-sm px-2.5 py-1` (more visible, slightly bigger hit area)
- Summary: `text-base text-surface-300`
- Meta row: `text-sm`
- Card padding: `p-5` or `p-6`
- Add subtle shadow: `shadow-sm hover:shadow-md`
- Button: `px-5 py-2.5 text-base`

### 5. InvestigationPage (`pages/InvestigationPage.jsx`)
- **Drag handle:** Increase from `w-1` to `w-1.5`, hover to `w-2`. Consider adding a visible grip indicator (3 vertical dots or lines) centered on the handle using a pseudo-element or an inline SVG icon
- The drag handle should have a larger invisible hit area — wrap in a `w-3` container with the visible bar centered

### 6. CaseHeader (`components/investigation/CaseHeader.jsx`)
- Subject user ID: `text-base font-mono font-semibold`
- Badges: `text-sm px-2.5 py-1`
- Summary: `text-sm text-surface-400` (this is secondary, sm is fine here)
- Padding: `px-5 py-4`

### 7. CaseDataTabs (`components/investigation/CaseDataTabs.jsx`)
- Tab text: `text-sm font-medium` (up from `text-xs`)
- Tab padding: `px-4 py-3` (up from `px-3 py-2`)
- Active tab: thicker border `border-b-[3px]` instead of `border-b-2`
- Inactive tabs: add `hover:bg-surface-700/50` for hover feedback
- Container padding: `px-3`

### 8. CaseDataPanel (`components/investigation/CaseDataPanel.jsx`)
- Padding: `p-5` or `p-6`
- The MarkdownRenderer handles content styling — ensure prose sizing is adequate (see MarkdownRenderer below)

### 9. MarkdownRenderer (`components/shared/MarkdownRenderer.jsx`)
- Ensure the prose wrapper uses `prose-base` not `prose-sm`
- Tables: add `rounded overflow-hidden` wrapper, ensure cell padding is comfortable
- Code blocks: slightly larger text
- Headings in rendered markdown should have clear visual weight

### 10. ChatMessageList (`components/investigation/ChatMessageList.jsx`)
- Message spacing: `space-y-5` (up from `space-y-4`)
- Padding: `p-5`

### 11. ChatMessage (`components/investigation/ChatMessage.jsx`)
- **User messages:**
  - Text: `text-base`
  - Role label: `text-sm font-semibold`
  - Timestamp: `text-xs text-surface-500`
  - Max width: keep `max-w-[85%]`
  - Slightly more padding: `px-5 py-4`
- **Assistant messages:**
  - Same sizing as user messages
  - Role label: `text-sm font-semibold`
  - Content rendered via MarkdownRenderer — ensure prose base size
  - Slightly more padding: `px-5 py-4`
- **Tools used footer:**
  - `text-sm` (up from `text-xs`)
  - Consider making document titles clickable in future (not this pass)

### 12. ChatInput (`components/investigation/ChatInput.jsx`)
- Textarea: `text-base`, increase `rows={3}`
- Container padding: `px-5 py-4`
- Send button: `px-5 py-2.5 text-base font-medium`
- Placeholder text: `text-base`

### 13. StreamingIndicator (`components/investigation/StreamingIndicator.jsx`)
- Dots: `w-2 h-2` (up from `w-1.5 h-1.5`)
- Text: `text-sm` (fine as-is, it's secondary)
- Padding: `px-5 py-3`

### 14. ImageUpload (`components/shared/ImageUpload.jsx`)
- Review thumbnail sizes — ensure they're at least 48x48
- Remove button should be clearly visible

### 15. LoadingSpinner (`components/shared/LoadingSpinner.jsx`)
- Sizes may need review — ensure `lg` is visibly large

---

## Colour & Depth

The current palette is fine (primary blue + surface slate). What's missing is **depth and layering**:

- **Header bar:** Add `shadow-md` to separate from content
- **Case cards:** Add `shadow-sm`, `hover:shadow-md` with transition
- **Chat message bubbles:** Consider very subtle shadow `shadow-sm`
- **Login card:** `shadow-xl` for floating effect
- **Modals/overlays (future):** `shadow-2xl`
- **Drag handle:** Subtle glow on hover, e.g., `hover:shadow-[0_0_6px_rgba(14,165,233,0.3)]`

---

## Transitions & Micro-interactions

Add `transition-all duration-200` where missing:
- Card hover states
- Tab hover/active states
- Button hover states
- Badge hover states (if any become interactive)

---

## Summary of File Changes Required

| File | Key Changes |
|------|-------------|
| `AppLayout.jsx` | Bump font sizes, add header shadow, larger back arrow |
| `LoginPage.jsx` | Larger title, input, button; card shadow + accent border |
| `CaseListPage.jsx` | Add page title/count, increase card gap |
| `CaseCard.jsx` | Bump all font sizes, more padding, add shadow |
| `InvestigationPage.jsx` | Wider drag handle with grip indicator |
| `CaseHeader.jsx` | Bump font sizes, more padding |
| `CaseDataTabs.jsx` | Larger tabs, thicker active border, hover states |
| `CaseDataPanel.jsx` | More padding |
| `MarkdownRenderer.jsx` | Ensure prose-base sizing |
| `ChatMessageList.jsx` | More spacing between messages |
| `ChatMessage.jsx` | Bump font sizes, more padding |
| `ChatInput.jsx` | Larger textarea and button, text-base |
| `StreamingIndicator.jsx` | Slightly larger dots |
| `ImageUpload.jsx` | Review thumbnail sizes |

**No logic changes. No new components. No structural changes. Pure Tailwind class adjustments.**
