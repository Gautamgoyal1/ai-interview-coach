# UI/UX Phase 1: trust and usability fixes

Date: 14 November 2026. This phase preserves the existing cream, charcoal, and
terracotta design system. It does not redesign the page hierarchy.

## Audit findings addressed

- **Reports and practice:** topic percentages are no longer labelled `/5`;
  dimension ratings retain their actual `/5` scale. HR topics use behavioral
  labels, and every report practice entry passes the track, report ID, report
  session ID, role, and relevant gap. Recommendation launches keep their source.
  A reloaded practice URL retains its originating context. Reopened sessions use
  the existing report-list API to resolve numeric report IDs to session IDs;
  unresolved/deleted sources lead honestly to the Reports list, never `/reports/1`.
- **Incomplete grading:** the overall score now shows graded-answer coverage
  alongside it. Unavailable scores remain unavailable; no grading data or rubric
  weights were changed.
- **Temporary state:** report-roadmap and resume-improvement checkmarks explicitly
  state that they reset when leaving the page.
- **Resume Analyzer:** shrinking grid columns/fields and wrapping upload text
  prevent mobile overflow. Unknown evidence is a separate category; a matched
  skill without evidence metadata is not called demonstrated or mentioned-only.
  Reuse says "Opened saved analysis" and reanalysis says "Analyze Again".
- **Dashboard:** independent settled requests keep healthy panels and previously
  loaded data. Failed histories are unavailable rather than empty/zero, with Retry.
  Counts say "Recent Resume Profiles" and "Recent Reports", reflecting bounded
  result sets instead of claiming total completed interviews.
- **Practice recovery:** sessions and recommendations load independently. Retry
  repeats failed loading; a failed session creation leaves loading and can be
  retried explicitly. Creation from a query is guarded against duplicate mounting.
- **Accessibility:** practice inputs/selects have associated labels; practice and
  interview answer fields have explicit accessible names. Setup selections expose
  pressed state. Dialogs and mobile navigation contain focus, handle Escape,
  restore the trigger, make background branches inert, and lock background scroll.
  Closed mobile navigation is inert. Profile and theme controls are sibling
  interactions rather than a button nested in a link.
- **Accuracy and consent:** the unconditional email "Verified" badge is removed.
  Setup points users to Practice Mode for hints. Resume/history/dashboard shortcuts
  select a profile in Setup and require an explicit start, rather than automatically
  launching a voice interview.

## Files changed in this phase

- `frontend/src/utils/practiceNavigation.ts`
- `frontend/src/hooks/useModalFocus.ts`
- `frontend/src/components/ActionMenu.tsx`
- `frontend/src/components/ConfirmDialog.tsx`
- `frontend/src/components/Layout.tsx` and `Layout.css`
- `frontend/src/features/interview/AnswerBox.tsx` and `InterviewSetup.tsx`
- `frontend/src/features/reports/TopicScores.tsx`, `PracticePlan.tsx`, `MissedPoints.tsx`
- `frontend/src/features/resume/ResumeReport.tsx`
- `frontend/src/pages/Dashboard.tsx`, `PracticeWorkspace.tsx`, `Report.tsx`
- `frontend/src/pages/InterviewRoom.tsx`, `Profile.tsx`, `ResumeAnalysis.tsx`
- `frontend/src/pages/ResumeAnalysis.css`
- `frontend/tests/phase1Trust.test.tsx`
- `scripts/verify_ui_phase1.mjs`
- This verification note.

Pre-existing uncommitted changes were preserved. No dependencies were added in
this phase. Backend logic, schema, authentication implementation, and Azure
recognition/synthesis implementation were not modified.

## Verification

- Complete frontend suite: **31 passed**, including five new unit regressions.
- TypeScript and Vite production build: **passed**. Existing bundle-size warning remains.
- Offline Edge browser: **13 grouped checks passed**, including four responsive
  widths; a separate failed-creation/retry regression also passed. The reusable
  browser script includes all 14 groups for future runs.
- Browser coverage: all report practice links preserve HR/source context; one
  practice creation per launch; reload/reopen/return navigation; partial coverage;
  independent dashboard and practice failures; actual Retry requests; explicit
  interview setup without a start or speech request; unknown evidence; focus
  containment/Cancel/Escape/trigger restoration; drawer keyboard loops and backdrop
  dismissal; labels; account-email accuracy; control bounding boxes.
- Widths: **320, 375, 768, 1440 px**. All visible main-page interactive controls
  were checked for horizontal bounds on captured pages. Analyzer controls were
  additionally inspected directly. No horizontal document overflow was found.
- No real API data was modified by browser tests; API responses were intercepted
  with synthetic fixtures. No paid Azure calls were made. Backend tests were not
  rerun because backend code and API contracts were unchanged by this phase.

Run again from the repository root:

```powershell
node scripts/verify_ui_phase1.mjs
```

The browser script uses temporary Playwright tooling already installed under
`storage/voice-acceptance/node_modules` and the installed Edge executable. Frontend
unit/build commands remain `npm test` and `npm run build` from `frontend`.

## Screenshots

- Resume Analyzer mobile [before](../storage/ui-ux-audit/analyzer-375.png) /
  [after](../storage/ui-phase1/analyzer-375.png).
- [Analyzer at 320 px](../storage/ui-phase1/analyzer-320.png).
- [HR report with corrected units/context](../storage/ui-phase1/hr-report-1440.png).
- [Partial score coverage](../storage/ui-phase1/partial-report-1440.png).
- [Healthy dashboard panel during a failure](../storage/ui-phase1/dashboard-partial-1440.png).
- [Practice Hub partial failure](../storage/ui-phase1/practice-partial-1440.png).
- [Keyboard-contained mobile drawer](../storage/ui-phase1/drawer-320.png).
- [Browser regression results](../storage/ui-phase1/regression-results.json).

Artifacts are ignored local test output, not production assets.

## Remaining limitations and Phase 2

- For legacy/reopened practice sessions without a return URL, source lookup can
  resolve only the most recent 100 report summaries exposed by the existing API.
  If unavailable, the link goes to the Reports list. Newly launched report-origin
  practice URLs carry the session identifier directly and do not depend on lookup.
- Checkmarks intentionally remain temporary; this phase adds no progress persistence.
- Human microphone/listening acceptance is still outstanding; these UI changes do
  not substitute for it.
- Phase 2: shorten Interview Setup, distinguish configuration from intentional
  quick-start affordances, unify navigation naming, and prioritize one meaningful
  next task on the dashboard. Later workspace work can reduce repeated report
  sections and mobile question/answer scrolling without altering speech lifecycle.
- Screen-reader/device coverage beyond the keyboard/browser checks is not complete.

No commits, pushes, or merges were performed.
