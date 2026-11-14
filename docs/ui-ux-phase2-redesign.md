# UI/UX Phase 2: Dashboard and Interview Setup

Date: 14 November 2026.

## Design changes

### Dashboard: preparation command center

The target role is the page heading, with a small personal introduction rather
than a large greeting card. One warm editorial band presents one primary action.
The next action is chosen from available data:

1. A relevant practice gap for the current role, ordered by priority.
2. A configured interview when a resume for that role is available.
3. Topic practice when an interview report exists without a matching resume/gap.
4. Resume analysis for a new preparation goal.
5. Explicit reconnect/unavailable guidance if no useful information loaded.

Report review remains a supporting link, not an endlessly repeated primary task.
Recommendations for other target roles do not silently take over the current goal.
Practice links retain Phase 1 source-report and track context.

Resume alignment and interview performance are separate evidence sections. Scores
retain their actual units; missing scores are unavailable. Counts explicitly refer
to the most recent fetched profiles/reports, up to ten, rather than lifetime totals.
A dated activity list opens saved work, with a compact practice-focus list alongside.
There are no decorative analytics, invented trends, nested feature cards, gradients,
or new typography dependencies.

Each data source now renders independently while other sources are still loading.
A failed panel retains previously fetched information, explains its unavailable
state, and offers Retry. Stale/unmounted requests are ignored. The recommended
primary action waits for the current overview request set to settle.

### Interview Setup: focused configuration workspace

- Resume/profile context comes first, with a labelled native select and source link.
- Native radio groups choose Technical/HR and Text/Voice. Text is the default;
  Voice is an explicit choice. No start, speech request, or microphone operation
  occurs just by visiting setup or selecting a format.
- Experience defaults to the existing profile enum. Starting difficulty follows
  the existing calibration policy: Easy for internship, Medium otherwise. Once
  manually customized, difficulty is not overwritten by experience changes.
- All question counts (5, 8, 10), difficulties, experience levels, and adaptive/mock
  options remain available. Progression uses a native Advanced settings disclosure.
- A concise launch summary is beside the form and sticky on desktop. On smaller
  screens it follows the shortened form in normal document flow, avoiding a fixed
  overlay on fields or the mobile keyboard.
- Starting is explicit and guarded while the existing parent start request runs.
  The API request body remains unchanged. Loading/error states disable launch;
  Retry preserves the configuration. New users receive a resume-analysis action
  and a secondary Practice Hub path.

Representative fixture captures: setup measured 1,258 px at 1440 px wide and
1,919 px at 375 px wide, versus the earlier long-form captures of approximately
2,599 and 5,019 px. These are screenshot-content measurements, not timings or
conversion claims; profile selection/text can affect exact height.

## Files updated

- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/Dashboard.css` (shared legacy headings retained for Practice)
- `frontend/src/features/interview/InterviewSetup.tsx`
- `frontend/src/features/interview/InterviewSetup.css` (new isolated stylesheet)
- `frontend/tests/phase2Preparation.test.tsx` (eight new unit regressions)
- `scripts/verify_ui_phase2.mjs` (offline responsive and interaction regression)
- `scripts/verify_ui_phase1.mjs` (selectors adapted to the native setup controls)
- This report.

Backend/API contracts, LangGraph, grading, Azure speech lifecycle, Practice Mode
internals, and unrelated page implementations were not changed. Existing working
changes were preserved. No application dependencies were added. A temporary
formatter was used without modifying package manifests.

## Verification

| Check | Result |
|---|---|
| Complete frontend suite | 39 passed, including 8 new Phase 2 tests |
| TypeScript and Vite production build | Passed; existing bundle-size warning remains |
| Existing Phase 1 browser regression | 14 grouped checks passed |
| Phase 2 browser regression | 9 grouped checks passed |
| Additional native radio arrow-key check | Passed |
| Widths | 320, 375, 768, 1440 px |
| Empty/loading/error states | Both pages checked at every width |
| Partial-failure dashboard | Checked at every width; healthy sections remain usable |
| Setup error and Retry | Passed; launch unavailable until resumes load |
| Technical/Text/Adaptive start | Passed, existing API contract and mode URL |
| HR/Voice/Mock start | Passed, exact API payload and one request despite double-click |
| Setup without explicit start | No interview start or speech request |
| Keyboard | Native radio arrows, labels, select controls, disclosure Enter activation |
| Bounds | Visible main-page controls remain inside horizontal viewport; no document overflow |

Browser captures use the running frontend in Edge with intercepted synthetic API
responses. They do not mutate actual account data or call paid Azure services.
The voice launch response was intercepted too; this verifies configuration and
navigation, not a new live speech acceptance run. Backend tests were not rerun
because this phase changes no backend implementation or API contract.

Run from repository root:

```powershell
node scripts/verify_ui_phase2.mjs
node scripts/verify_ui_phase1.mjs
```

These browser scripts use the temporary Playwright tooling under
`storage/voice-acceptance/node_modules` and the installed Edge executable. Run
`npm test` and `npm run build` from `frontend` for unit/build checks.

## Before/after evidence

| Page | Before | After |
|---|---|---|
| Dashboard desktop | [Before](../storage/ui-phase2/before-dashboard-1440.png) | [After](../storage/ui-phase2/dashboard-1440.png) |
| Setup desktop | [Before](../storage/ui-phase2/before-setup-1440.png) | [After](../storage/ui-phase2/setup-1440.png) |
| Setup mobile | [Before](../storage/ui-phase2/before-setup-375.png) | [After](../storage/ui-phase2/setup-375.png) |

- [All responsive screenshots](../storage/ui-phase2/screenshots.md)
- [Phase 2 browser results and request bodies](../storage/ui-phase2/results.json)
- [Native keyboard results](../storage/ui-phase2/keyboard-results.json)

Screenshots and raw results are ignored local review artifacts, not shipped assets.

## Remaining UX work

- Mobile setup still requires scrolling through the configuration; its launch
  action deliberately stays in flow instead of obscuring fields with a fixed bar.
- Goal relevance uses case-insensitive role-name matching; no speculative mapping
  between differently named roles or invented progress metrics was introduced.
- Overview data remains bounded by existing APIs. No lifetime totals or activity
  beyond those saved resume/report results are implied.
- Shared navigation naming, report/practice workspace density, and global component
  polish remain later work. Legacy setup CSS in the shared interview-room stylesheet
  was left alone to avoid disturbing that separately verified workspace.
- Physical-device, full screen-reader and human microphone/listening acceptance
  remain separate checks. No accessibility conformance claim is made from these
  browser checks alone.

No commits, pushes, or merges were performed.
