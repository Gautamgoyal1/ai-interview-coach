> Light mode remains current. The newer [dark-only polish](dark-theme-polish.md) supersedes the midnight/periwinkle dark palette below.

# PrepMate theme refinement

18 November 2026. Presentation-only refinement of the existing Ink and Amber theme.
The rejected Deep Slate experiment remains reverted. Existing layout, typography,
content, state, routes, API integrations and business logic are preserved.

## Light mode

Warm cream canvas (`#FAF8F4`), warm paper cards (`#FFFDFA`) and existing amber actions
(`#FFB020`). Supporting surfaces use pale sage (`#EDF4EF`), powder blue (`#EDF2FA`),
soft lavender (`#EFEAF8`) and a restrained peach selection surface (`#F8EEE7`).
These roles color existing panels rather than adding decorative components.
Navigation uses warm stone; secondary labels and chart series use readable blue,
teal and rose companions. Success, warning and error retain their semantic roles.

## Dark mode

Midnight ink canvas (`#111628`) and indigo cards (`#1A2032`) replace neutral grey.
Periwinkle (`#B2BAFF`) replaces yellow for primary actions, progress, active states
and focus outlines. Buttons retain a dark foreground (`#171B30`). Blue question
panels, muted teal coaching surfaces and plum highlights provide separation.
Readable off-white headings, brighter secondary text and stronger control borders
keep surfaces distinct without gradients or glow. Existing appearance selection
and profile previews remain functional.

## Implementation

All application color changes are confined to `frontend/src/styles/tokens.css`.
The existing semantic aliases apply them across public, authentication, dashboard,
resume, interview setup, Text/Voice rooms, reports, history, practice and profile.
`frontend/tests/designTokens.test.ts` now checks the separate light/dark accents
while preserving text, action, status, control, focus and chart contrast checks.
No dependencies, backend changes, paid API calls or physical microphone tests.

Local backups, screenshots and test logs are stored under ignored
`storage/ui-identity/ink-refined/`. Browser checks use isolated headless Edge
with mocked API and speech responses. They are not live Azure acceptance tests
or a full assistive-technology/device certification.

## Verified results

- 61 frontend tests passed; TypeScript and Vite production build passed.
- Existing bundle-size warning remains (main JavaScript approximately 749 kB).
- 15 page variants at 320, 375, 768 and 1440 px in both themes: 120 captures,
  1,132 rendered control checks and 5,970 text contrast samples.
- 22 additional empty/loading/error/partial-result captures; 10 keyboard and
  validation checks, including drawer/dialog focus containment and restoration,
  menu focus, visible form focus, hover feedback and reduced motion.
- No detected text contrast failures, viewport overflow, out-of-bounds controls or
  page runtime errors in the final captures. The comparison table retains its
  intended contained horizontal scrolling and keyboard access.
- 208 backend Python source/test hashes match the pre-theme baseline.
- No Git commits, pushes, deployments or database changes.

`storage/ui-identity/ink-refined/verification.json` records the local verification.
Page images are in `after/`; dialog/drawer and feedback images are in `states/`.
