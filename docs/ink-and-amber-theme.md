> The current light/dark refinements are documented in [Ink theme refinement](ink-theme-refinement.md). The original palette and verification below are retained as historical evidence.

# PrepMate ? Ink and Amber

17 November 2026. Implements the supplied ink-and-amber palette across the existing
frontend. Prior uncommitted work and historical design evidence are preserved.

## Visual rules

| Token | Light | Dark |
|---|---|---|
| `--bg` | `#FAF8F4` | `#0F1318` |
| `--card` | `#FFFFFF` | `#171C23` |
| `--border` | `#E6E1D8` | `#262E38` |
| `--text` | `#14181F` | `#ECEFF3` |
| `--muted` | `#66707C` | `#8F9BA8` |
| `--accent` | `#FFB020` | `#FFB020` |
| `--on-accent` | `#1B1204` | `#1B1204` |

Canonical variables map to the existing semantic token system. Amber is the fill
for primary actions and progress, with restrained active-state highlights. Large
content surfaces remain neutral. There is no arbitrary per-page accent color.
Muted green/red retain their success/error meaning and labels.

`--accent-ink` is an ink foreground, not amber. Text, links and icons never inherit
the amber fill color in light mode. Amber buttons use `--on-accent`, not white.
Navigation foregrounds also remain readable ink. Decorative panel rules are 1px;
contrasting keyboard outlines remain 2px and active navigation has an amber marker.

Gradients, drop shadows and glow effects are removed. Focus rings are flat outlines,
loading placeholders use flat neutral fills, and menus/dialogs keep their thin
boundaries. Existing reduced-motion support and restrained presentation transitions
remain. No animation changes application state.

The resume score ring now uses SVG circle strokes instead of a conic gradient. Its
existing percentage, accessible progress value and numeric display are unchanged;
regressions cover 0%, fractional and 100% scores. Amber progress has a thin darker
edge on light surfaces; the numerical value remains available independently of color.

## Scope

Updated shared tokens, buttons/forms, navigation, landing/auth, Dashboard, setup,
Interview Room, resume/saved analysis, reports, history, practice and profile previews.
Both light and dark modes use the same semantic roles. The favicon is neutral ink.

No backend APIs, database schema/data, grading/scoring, question generation, RAG,
authentication state, interview state or voice hooks were changed. The score-ring
change is presentation only. No dependency was added. No live Azure/Gemini calls or
physical microphone acceptance test is part of this task.

## Local evidence

Evidence and backups are under ignored `storage/ui-identity/ink-amber/`.
`verification.json` is the final check receipt. Browser verification uses local
headless Edge, an isolated temporary profile, mocked APIs and mocked Speech SDK.
It does not certify full WCAG conformance or physical-device/browser compatibility.

| View | Light | Dark |
|---|---|---|
| Dashboard | [Light](../storage/ui-identity/ink-amber/final/dashboard-light-1440-viewport.png) | [Dark](../storage/ui-identity/ink-amber/final/dashboard-dark-1440-viewport.png) |
| Interview | [Light](../storage/ui-identity/ink-amber/final/interview-light-375-viewport.png) | [Dark](../storage/ui-identity/ink-amber/final/interview-dark-375-viewport.png) |
| Setup | [Light](../storage/ui-identity/ink-amber/final/setup-light-1440-viewport.png) | [Dark](../storage/ui-identity/ink-amber/final/setup-dark-1440-viewport.png) |
| Practice | [Light](../storage/ui-identity/ink-amber/final/practice-light-375-viewport.png) | [Dark](../storage/ui-identity/ink-amber/final/practice-dark-375-viewport.png) |
| Resume | [Light](../storage/ui-identity/ink-amber/final/resume-light-1440-viewport.png) | [Dark](../storage/ui-identity/ink-amber/final/resume-dark-1440-viewport.png) |
| Report | [Light](../storage/ui-identity/ink-amber/final/report-light-375-viewport.png) | [Dark](../storage/ui-identity/ink-amber/final/report-dark-375-viewport.png) |
| Landing | [Light](../storage/ui-identity/ink-amber/final/landing-light-1440-viewport.png) | [Dark](../storage/ui-identity/ink-amber/final/landing-dark-1440-viewport.png) |

Links are local review artifacts, not published downloads. The existing bundle-size
warning remains. Safari/Firefox, screen readers, physical devices and live microphone
acceptance require separate verification. Changes are not committed or pushed.

## Final verification results

- **61 frontend tests passed** across 7 files; TypeScript and Vite build passed.
- **120 final route/theme/viewport cases passed**: 15 views at 320, 375, 768 and 1440px, light and dark.
- **1,132 rendered-control checks**: no incorrect foregrounds on amber buttons,
  no painted control shadows, no unnamed visible buttons and no light-mode amber text.
  This counts repeated controls across viewports, not unique button implementations.
- No final horizontal overflow, clipped controls, unnamed form inputs, sampled-text
  contrast failures or browser runtime errors.
- **22 additional state captures and 10 keyboard/hover/validation checks passed**, including
  flat focus outlines, drawer/dialog focus containment, menus and reduced motion.
- **8 mocked interview/practice groups passed in each theme**: final transcript completion,
  explicit single submission, permission denial, rapid mode switching, hints/reference
  assistance, coaching retries and report-to-practice navigation.
- Whitespace checks passed. No source changes to backend, services, authentication state,
  speech hooks, interview state, question generation or grading. No paid API calls or
  database writes. No Git staging, commit, push, merge or deployment.

Earlier contrast checks caught a derived light surface that was slightly too dark
for the supplied muted text. The derived surface was lightened; the supplied base
variables were kept exact. Keyboard focus was explicitly retained after glow removal.
The existing large-bundle warning remains in the production build log.

## Files changed in this iteration

- `frontend/public/favicon.svg`
- `frontend/src/index.css`
- `frontend/tests/designTokens.test.ts`
- `frontend/tests/phase1Trust.test.tsx`
- `frontend/src/components/Layout.css`
- `frontend/src/components/OverlayControls.css`
- `frontend/src/components/ThemeToggle.css`
- `frontend/src/pages/Dashboard.css`
- `frontend/src/pages/History.css`
- `frontend/src/pages/InterviewRoom.css`
- `frontend/src/pages/InterviewWorkspace.css`
- `frontend/src/pages/Landing.css`
- `frontend/src/pages/Practice.css`
- `frontend/src/pages/PracticeLearning.css`
- `frontend/src/pages/Profile.css`
- `frontend/src/pages/Profile.tsx`
- `frontend/src/pages/Report.css`
- `frontend/src/pages/ResumeAnalysis.css`
- `frontend/src/styles/motion.css`
- `frontend/src/styles/tokens.css`
- `frontend/src/features/interview/InterviewSetup.css`
- `frontend/src/features/resume/ResumeReport.tsx`
- `docs/ink-and-amber-theme.md`
- `docs/theme-refinement.md`
- `docs/visual-identity-redesign.md`
