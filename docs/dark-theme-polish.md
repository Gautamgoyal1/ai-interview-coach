# PrepMate dark-theme polish

18 November 2026. This change follows the supplied dark-only specification.
The light-theme token block is preserved byte for byte. Shared page layout,
content, routes, React state, API integrations and business logic are unchanged.
The sole non-color exception is single-line sidebar email truncation and a full-address title.

## Theming mechanism and scope

`ThemeContext.tsx` reads the `prepmate-theme` preference and applies
`data-theme="dark"` to the document element. The existing `.dark` class is retained.
Dark colors remain in the existing `styles/tokens.css` dark block; the new
`styles/dark.css` has only `html[data-theme="dark"]` selectors and is imported
from `index.css`. No Tailwind, theme dependency or component framework was added.

## Final dark token table

| Token | Value | Purpose |
|---|---|---|
| `--bg` | `#0F1318` | Page and sidebar |
| `--card` | `#171C23` | Cards and panels |
| `--elevated` | `#1E252E` | Inputs, dropzone, hover rows and floating menus |
| `--border` | `#262E38` | Decorative hairlines and dividers |
| `--border-strong` | `#646F7C` | Accessible input/dropzone edges |
| `--chart-track` | `#3A4552` | Dim data tracks |
| `--text` | `#ECEFF3` | Headings and primary text |
| `--text-secondary` | `#B4BDC9` | Descriptions |
| `--text-muted` | `#8F9BA8` | Helpers, placeholders and captions |
| `--accent` | `#FFB020` | Main actions, progress and active states |
| `--accent-hover` | `#FFC14D` | Primary action hover |
| `--accent-pressed` | `#E69A00` | Primary action press |
| `--on-accent` | `#1B1204` | Primary action foreground |
| `--accent-soft` | `rgb(255 176 32 / 12%)` | Active selection and drag-over |

Input borders are lifted from the proposed `#3A4552` to `#646F7C`: the supplied
shade falls below 3:1 on elevated controls; the adjusted shade reaches 3.02:1.
Decorative dividers keep the dim requested value. Chart tracks use `#3A4552`
so both amber and status data marks retain at least 3:1 contrast.

Success `#4ADE9A`, warning `#F2C14E`, danger `#FF7A7A` and info `#6CB4FF`
use 14% background tint and 30% border tint. Existing evidence classification
and matched/missing meaning are preserved. No new evidence labels are inferred.
Neutral badges use elevated fill, muted text and hairline borders; amber tint
is reserved for active states. Existing secondary actions in navigation,
history rows and targeted-practice setup are visually de-emphasized.

The upload zone uses elevated neutral fill. Its selected-file state remains
neutral, with the existing check icon in a success-tinted status tile. The
existing validation, replacement controls and button-disable rules are preserved.
Focus uses a flat 2px amber outline with 2px offset. Floating menus and dialogs
alone use a subtle shadow. There are no gradients, glows or decorative blur.

## Files changed for this task

- `frontend/src/styles/tokens.css`: dark token block only; no light values changed.
- `frontend/src/styles/dark.css`: scoped shared/component presentation rules.
- `frontend/src/index.css`: imports the scoped stylesheet.
- `frontend/src/components/Layout.tsx`: full-address title and email-only class.
- `frontend/src/components/Layout.css`: single-line ellipsis for that email class.
- `frontend/tests/designTokens.test.ts`: alpha compositing, semantic contrast,
  frozen light-token digest and dark-selector isolation regressions.
- `frontend/tests/sidebarProfile.test.tsx`: full email remains available; target-role
  content and wrapping remain unchanged.
- This report and the historical refinement report's current-theme pointer.

Existing uncommitted work is preserved. No backend or database changes, no paid
API calls, and no Git commits or pushes are part of this task.

## Contrast and verification method

The throwaway `storage/ui-identity/dark-polish/check_contrast.py` checks 174
semantic foreground/background/backing-surface combinations, compositing
translucent tints over page, card and elevated surfaces. All pass. Minimum
body-text contrast is 5.46:1; action/status text 4.90:1; focus 8.45:1;
control boundaries 3.02:1. Browser contrast sampling additionally checks
actual rendered text against composed ancestor backgrounds.

Original moving-screen captures showed minor caret/wave/animation-frame
variation. Deterministic comparisons freeze animations and hide carets in
both copies. An isolated pre-change source copy and the current app produce
60 pixel-identical light screenshots (15 page variants at 375 and 1440 px,
full-page and viewport images). No application CSS is altered for this comparison.
The only stylesheet injected by the test disables animation, transitions and carets
in both copies. Original and deterministic evidence are both retained locally.

All local screenshots, backups, comparison output and test logs are under the
ignored `storage/ui-identity/dark-polish/` directory. API and Speech SDK responses
are mocked; no live Azure, Gemini or microphone acceptance test is claimed.

## Final regression results

- 66 frontend tests passed across 8 files. TypeScript and Vite production build passed.
- Existing production bundle-size warning remains (main JavaScript about 749 kB).
- No lint command/configuration or lint dependency is configured, so lint was not
  claimed or installed as part of this presentation-only task.
- 120 route/theme/width cases cover 15 page variants at 320, 375, 768 and 1440 px
  in light and dark, with 1,132 controls and 5,970 text samples checked.
- 22 additional empty/loading/error/partial-result captures and 10 keyboard/validation
  checks pass, including focus containment/restoration, hover, validation and reduced motion.
- 38 focused checks pass: upload drag/invalid/selected states; enabled, hover and
  pressed Analyze Resume; mocked loading, failure and recovery; evidence color mapping;
  long email truncation/title in both themes at all four widths; and primary-action
  emphasis moving from coaching to submission when an improved answer is typed.
- Resume form reanalysis is visually secondary after results arrive. Coaching retry
  is visually secondary while a new practice response is being edited. No handlers,
  submission rules or API payloads changed.
- All 60 deterministic light screenshots are pixel-identical. The normal captures'
  small moving-frame differences remain archived rather than being relabeled as passes.
- Source checks confirm no literal presentation colors outside the central tokens,
  no new dependencies, and 208 backend Python files unchanged against the baseline.
- Final browser captures have no detected text-contrast, horizontal page-overflow,
  out-of-bounds control, bright-divider or page-runtime failures.

These are Chromium/Edge desktop automation results with mocked services, not
full WCAG certification, screen-reader testing, physical tablet/mobile testing,
Safari/Firefox testing or live microphone/provider verification. Native OS file
picker and title-tooltip rendering were not visually validated. The full address
and native title attribute were verified without truncating the underlying value.

The machine-readable receipt is `storage/ui-identity/dark-polish/verification.json`.
Before/current images are in `before/`, `after/` and `recheck/`; deterministic light
pairs are in `frozen-light/`; focused interaction screenshots are in `details/`;
keyboard/error-state screenshots are in `states/`. All are local ignored evidence.
