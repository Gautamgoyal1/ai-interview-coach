# Voice release blocker fixes — 14 November 2026

The two bugs in [the acceptance baseline](voice-mode-acceptance-report.md) have
been fixed. Human microphone/listening acceptance remains pending.

## Changes

- `backend/app/modules/interview/service.py`: retrieve the submitted question's
  evaluation by its ID from `evaluation_history`, instead of transient
  `current_evaluation`. New-question generation resets the transient field, but
  retains evaluation history. Save the selected grade, answer, and advanced graph
  state in the existing database transaction. Missing grades are explicitly
  unavailable with no invented score. Existing duplicate guards remain intact.
- `frontend/src/pages/InterviewRoom.css`: below 640 px, wrap the header and its
  actions. End interview remains a native, keyboard-accessible button. Desktop
  styles are unchanged.
- `backend/tests/integration/test_evaluation_persistence.py`: eight combinations
  of Technical/HR, follow-up/no-follow-up, and grading success/failure; plus a
  missing-history isolation test. Tests cover primary-to-next, primary-to-follow-up,
  follow-up-to-next, completion, checkpoint loss, refresh, duplicate requests,
  turn-specific grades, rubric association, and persisted report coverage.
- `scripts/verify_interview_header.mjs`: offline browser regression using mocked
  backend responses at 320, 375, 390, 768, and 1440 px. Checks actual control bounds,
  horizontal overflow, Tab/Enter activation of End interview, and completed-session
  header bounds. Uses the locally installed temporary Playwright tooling, or
  `PREPMATE_PLAYWRIGHT_MODULE`; browser location can be overridden with
  `PREPMATE_BROWSER_PATH`.

## PostgreSQL verification

Ran the nine new regressions in the running backend container with
`PREPMATE_PERSISTENCE_POSTGRES=1`. Eight database scenarios each create their own
unique temporary schema. Tests read turns through fresh SQLAlchemy sessions after
submission and duplicate attempts, compare grades with the matching question ID,
then generate and read the stored report. All nine tests passed.

Successful grading gives full evaluated-answer coverage; failed grading remains
unavailable. Both Technical `v1.0` and HR `v1.0-hr` stay associated correctly.
Only generated test schemas are removed afterward. Application data, historical
scores, existing missing evaluations, and existing reports are not rewritten.

Run again:

```powershell
docker compose exec -T -e PREPMATE_PERSISTENCE_POSTGRES=1 backend python -m pytest tests/integration/test_evaluation_persistence.py -q -p no:cacheprovider
node scripts/verify_interview_header.mjs
```

## Browser verification

Final regression results: **259 backend tests passed**, **26 frontend tests
passed**, **9 new persistence tests passed in PostgreSQL mode**, and the
TypeScript/Vite production build passed. Existing warnings remain: the backend
HTTP 422 constant deprecation and the frontend bundle-size warning.

All five widths passed bounds and keyboard checks. Screenshots were inspected at
320 and 1440 px; the narrow header wraps and preserves End interview, and the
1440 px header retains its desktop layout. Artifacts are ignored test output:

- [320 px](../storage/voice-release-regression/header-320.png)
- [375 px](../storage/voice-release-regression/header-375.png)
- [390 px](../storage/voice-release-regression/header-390.png)
- [768 px](../storage/voice-release-regression/header-768.png)
- [1440 px](../storage/voice-release-regression/header-1440.png)
- [Exact control bounds and results](../storage/voice-release-regression/header-results.json)

No paid Azure calls were needed. No speech, rubric, adaptive generation, resume,
practice, authentication, or database-schema changes were made. No push or merge
was performed. Final human microphone and human-audible playback testing is still
the next acceptance gate; prior prerecorded Azure tests do not replace it.
