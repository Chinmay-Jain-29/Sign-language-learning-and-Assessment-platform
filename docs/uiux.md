# UI/UX Design System & Accessibility Specification (`docs/uiux.md`)

## 1. Design System Tokens & Aesthetics
The frontend design system is designed as a calm, accessible EdTech + AI application.

- **Primary Color**: `#0284C7` (Sky 600)
- **Primary Hover**: `#0369A1` (Sky 700)
- **Background Slate**: `#0F172A` (Slate 900)
- **Card Background**: `#1E293B` (Slate 800)
- **Surface Border**: `#334155` (Slate 700)
- **Text Primary**: `#F8FAFC` (Slate 50)
- **Text Muted**: `#94A3B8` (Slate 400)
- **Accent Emerald**: `#10B981` (Emerald 500)
- **Accent Rose**: `#F43F5E` (Rose 500)

---

## 2. 15 Webcam States (`WebcamStateIndicator.jsx`)
1. *Camera permission requested*
2. *Camera permission denied*
3. *Camera unavailable*
4. *No hand detected*
5. *Multiple hands*
6. *Multiple people*
7. *Partial hand*
8. *Poor visibility*
9. *Hand too far*
10. *Hand too close*
11. *Valid input*
12. *Processing*
13. *Prediction*
14. *Stable prediction*
15. *Assessment complete*

---

## 3. WCAG 2.1 AA Accessibility System (`AccessibilityContext.jsx`)
- **High Contrast Toggle**: Applies `.high-contrast` CSS overrides ($7:1\text{ contrast ratio}$).
- **Large Text Toggle**: Applies `.text-large` scaling all font sizes by $+20\%$.
- **Reduced Motion Toggle**: Applies `.reduced-motion` disabling CSS keyframe animations.
- **Focus States**: High-contrast outline focus rings (`2px solid #0284c7`).
- **Keyboard Navigation**: Full `Tab` key focus traps across modals, practice canvases, and role dashboards.
