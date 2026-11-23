> Historical design iteration. The current theme is documented in [Ink and Amber](ink-and-amber-theme.md); [Graphite Studio](theme-refinement.md) records the intermediate iteration. The green/terracotta/brass palette below has been superseded following user review.

# PrepMate ? Career Studio visual identity

Local implementation review, 17 November 2026. No commit, push, merge or deployment
is authorized for this change. Screenshots and browser-run logs are local evidence
under ignored `storage/ui-identity/`; they are not published verification downloads.

## Inventory before implementation

The frontend uses React/TypeScript/Vite and plain CSS, with a central token file
and a persisted light/dark ThemeContext. No Tailwind or component library is in
use. The audit found 174 literal color occurrences in ten source files, including
the old theme definitions. Colors outside the theme included recording controls,
practice errors, profile previews, success alerts, landing browser dots and shadows.
The favicon was still a blue ?IC? mark.

The shared base stylesheet loaded after page styles, allowing generic `.pm-card`
properties to override intended page treatments. The warm palette had pale metadata,
blue-gray text, a white navigation rail and several dark-mode foreground issues.
The before browser captures also exposed mobile hero controls outside the viewport
while document scroll-width checks passed.

## Palette

| Role | Studio Parchment / light | Forest Ink / dark |
|---|---|---|
| Canvas | `#F5F0E8` | `#18221C` |
| Paper / raised surface | `#FFFDF7` | `#202D24` |
| Primary text | `#222823` | `#F4F0E6` |
| Secondary text | `#535E50` | `#C1CAB7` |
| Muted text | `#58614F` | `#ACBAA2` |
| Signature terracotta action | `#AD4C32` | `#F19B7D` |
| Action hover | `#913C28` | `#FFB295` |
| Pine / secondary interactive | `#315A4B` | `#B9D1B0` |
| Olive | `#606A45` | `#C0CD9F` |
| Brass highlight | `#E1C78B` | `#E1C78B` |
| Navigation rail | `#233C32` | `#14251B` |
| Featured panel | `#29473D` | `#273C2F` |
| Success foreground | `#2F684A` | `#A6D1A8` |
| Warning foreground | `#87591D` | `#E7C584` |
| Danger foreground | `#A53632` | `#FFADA0` |
| Informational foreground | `#315E63` | `#A3CED0` |

Terracotta is intentionally darker than the suggested starting color so normal
text and white action labels meet the contrast target. Brass is reserved for ink
surfaces, navigation selection and the dashboard's featured action; it is not
used as body text on parchment. The dark theme uses warm readable light accents
with dedicated dark button foregrounds, rather than reusing white button text.

## Token architecture

`frontend/src/styles/tokens.css` is the single color source for application CSS
and JSX. Palette ingredients feed semantic surface, typography, action, selection,
focus, disabled, feedback, navigation, chart, difficulty, interviewer/candidate,
recording, playback, processing and review tokens. Light/dark preview swatches are
explicitly independent of the active theme. Legacy aliases remain only to preserve
existing component contracts. The standalone favicon necessarily contains its own
fixed brand asset colors.

Base CSS is imported before App/page styles. Page styles consume semantic tokens;
no new UI dependency or font download was added. Editorial headings use the local
Iowan/Palatino/Book Antiqua/Georgia serif stack; existing Inter/system body type
remains. CSS reduced-motion behavior includes the landing preview and scrolling.

## Page and component changes

- **Shared shell:** forest-ink rail, brass active marker, readable muted navigation,
  keyboard focus, quieter parchment topbar and editorial wordmark.
- **Dashboard:** a forest featured next action with a brass CTA; paired paper/olive
  evidence sections and open recent-activity rows. Existing recommendations,
  independent loading/errors and bounded-count labels are unchanged.
- **Interview setup:** paper configuration, pine selected options with a structural
  left marker, numbered sections and an olive launch summary. Native radio/select
  contracts, experience/difficulty options and explicit start are preserved.
- **Interview room:** a labeled interviewer question on a calm pine-tinted surface,
  a separate paper candidate editor, consistent playback and recording controls,
  and distinct recording/processing/review states with their existing text labels.
  `data-voice-state` is presentation-only; it does not drive the voice lifecycle.
- **Practice:** a question/editor workspace beside olive coaching; restrained
  hints, retry comparison and contextual report navigation. Scoring/assistance
  tracking are untouched.
- **Resume and saved analyses:** olive upload area, clearer paper form, semantic
  progress graphics, wrapping saved-report headings and corrected 320px sizing.
- **Reports/history:** editorial report headings, pine overall score, meaningful
  chart tokens, open report sections and ledger-style history surfaces. Numerical
  scores, legends, labels and partial-coverage notices remain available.
- **Profile:** pine identity band, neutral forms and truthful light/dark previews
  with accessible selected state; account behavior is unchanged.
- **Login/register:** shared noninteractive studio identity beside the existing
  forms, compact mobile composition, accessible input states and unchanged auth.
- **Public landing:** editorial hero type, varied paper/pine/olive sections, a
  restrained product preview, corrected hero/mobile navigation bounds and a
  keyboard-scrollable named comparison region. The blue legacy favicon is replaced
  by the existing graduation-cap identity in terracotta.
- **Shared controls:** semantic actions, dialogs, menu focus, notifications, fields,
  error/disabled styles and reduced-motion support.

## Verification

Final browser results and exact changed-file inventory are recorded in the local
`storage/ui-identity/verification.json` after verification completes. Source-level
regressions are `frontend/tests/designTokens.test.ts`: AA text pairings, meaningful
UI/data contrast and a guard against scattering literal colors through CSS/JSX.

These tests assess defined pairs, not complete WCAG conformance. Browser contrast
sampling uses computed foregrounds and composited ancestor fills; it does not
certify every possible content variant, image, overlay or assistive-technology flow.
The horizontally scrollable comparison table is intentional and keyboard reachable.

Browser runs use headless Microsoft Edge and synthetic API responses, including
mocked Speech SDK, microphone tracks and audio playback. They make no paid provider
calls and create no live interview/user data. They do not establish physical
microphone capture, human listening or real Azure acceptance. External font
requests are blocked in the screenshot fixture, exercising the fallback typeface.

## Review and remaining scope

The design uses ink/serif hierarchy, varied surfaces and a deliberate single next
action rather than gradients or equally weighted cards. The interview room remains
calm: terracotta is an action, recording has a labeled state, and metadata does not
compete with the question. The identity is coherent across workspace, public and
account pages; these are implementation judgments pending user design review.

Remaining work outside this visual task: Safari/Firefox and physical-device checks,
screen-reader/manual accessibility audit, live microphone/human-listening acceptance,
and any separate frontend bundle splitting. No production-readiness claim is made.
Backend, knowledge, grading, question generation, authentication state, services,
voice hooks and user data are unchanged. No new dependency was introduced.

## Final regression results

| Verification | Result |
|---|---|
| Frontend suite | 56 tests passed in 7 files |
| TypeScript / Vite build | PASS; existing large-chunk warning, 748.51 kB main JS |
| Major route matrix | 15 views ? 4 widths ? 2 themes = 120 passing observations |
| Widths / themes | 320, 375, 768, 1440px; Studio Parchment and Forest Ink |
| Bounds, document overflow, unnamed inputs, runtime errors | Zero failures in final matrix |
| Additional states | 22 loading/empty/error/partial observations; 10 keyboard/validation/hover checks |
| Interaction regressions | 8 groups each in light and dark, all passed |
| Reduced motion / comparison-table keyboard scroll | PASS |
| Whitespace | PASS |
| Protected implementation | 337 backend, knowledge, hooks, state and service files unchanged |
| Paid AI requests / live database writes | None |

The interaction groups cover Technical/HR playback, recording/processing/review,
final words, transcript editing and explicit single submission, denial recovery,
rapid cancellation/mode switches, unsent-answer navigation, progressive hints,
reference reveal, coaching failures, retries/comparison and report ? practice ?
report routing after refresh. Microphone and playback are mocked.

Earlier attempts are preserved in local evidence. They exposed selector mistakes
in the audit harness, intermittent navigation timeouts, three initial token-pair
contrast failures, mobile layout overflow, decorative-separator contrast, and an
upload selector that accidentally styled normal inputs. These were not counted as
passes. Final checks use explicit rendered-page readiness; below-the-fold landing
sections are scrolled into view. A final polish reran affected routes, including
solid resume inputs versus the dashed upload target and compact report spacing.
Latest passing observations and their stage of origin are recorded in the final
matrix. Semantic pairing tests and sampled rendered contrast are evidence, not a
complete WCAG certification.

## Screenshot review

These are local-only screenshot links, intentionally excluded from Git.

| View | Before | After |
|---|---|---|
| Dashboard, desktop | [Before](../storage/ui-identity/before/dashboard-light-1440-viewport.png) | [After](../storage/ui-identity/final/dashboard-light-1440-viewport.png) |
| Interview setup, desktop | [Before](../storage/ui-identity/before/setup-light-1440-viewport.png) | [After](../storage/ui-identity/final/setup-light-1440-viewport.png) |
| Interview room, dark/mobile | [Before](../storage/ui-identity/before/interview-voice-dark-375-viewport.png) | [After](../storage/ui-identity/final/interview-voice-dark-375-viewport.png) |
| Practice workspace, desktop | [Before](../storage/ui-identity/before/practice-light-1440-viewport.png) | [After](../storage/ui-identity/final/practice-light-1440-viewport.png) |
| Resume Analyzer, desktop | [Before](../storage/ui-identity/before/resume-light-1440-viewport.png) | [After](../storage/ui-identity/final/resume-light-1440-viewport.png) |
| Report, mobile | [Before](../storage/ui-identity/before/report-light-375-viewport.png) | [After](../storage/ui-identity/final/report-light-375-viewport.png) |
| Login, desktop | [Before](../storage/ui-identity/before/login-light-1440-viewport.png) | [After](../storage/ui-identity/final/login-light-1440-viewport.png) |
| Landing, mobile | [Before](../storage/ui-identity/before/landing-light-375-viewport.png) | [After](../storage/ui-identity/final/landing-light-375-viewport.png) |

Full-page versions are beside viewport captures. Additional images show drawer
focus, confirmation dialogs, validation, partial reports and mocked voice states.

## Changed files

- `.gitignore`
- `docs/visual-identity-redesign.md`
- `frontend/public/favicon.svg`
- `frontend/src/components/AuthIdentity.tsx`
- `frontend/src/components/Layout.css`
- `frontend/src/components/OverlayControls.css`
- `frontend/src/components/ThemeToggle.css`
- `frontend/src/features/interview/AnswerBox.tsx`
- `frontend/src/features/interview/InterviewSetup.css`
- `frontend/src/features/interview/QuestionCard.tsx`
- `frontend/src/index.css`
- `frontend/src/main.tsx`
- `frontend/src/pages/Dashboard.css`
- `frontend/src/pages/History.css`
- `frontend/src/pages/InterviewRoom.css`
- `frontend/src/pages/InterviewWorkspace.css`
- `frontend/src/pages/Landing.css`
- `frontend/src/pages/Landing.tsx`
- `frontend/src/pages/Login.tsx`
- `frontend/src/pages/Practice.css`
- `frontend/src/pages/PracticeLearning.css`
- `frontend/src/pages/PracticeWorkspace.tsx`
- `frontend/src/pages/Profile.css`
- `frontend/src/pages/Profile.tsx`
- `frontend/src/pages/Register.tsx`
- `frontend/src/pages/Report.css`
- `frontend/src/pages/ResumeAnalysis.css`
- `frontend/src/styles/tokens.css`
- `frontend/tests/designTokens.test.ts`
