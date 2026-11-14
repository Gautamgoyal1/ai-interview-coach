# PrepMate UI/UX Phase 3: Interview Room and Practice Workspace

Date: 14 November 2026

## Scope and outcome

The two active workspaces now share a focused question-and-response composition, restrained neutral surfaces, editorial question typography and the existing cream/charcoal/terracotta tokens. Dashboard, Interview Setup, the Practice Hub design and unrelated pages are preserved. No backend APIs, schemas, LangGraph, rubric weights, evaluation persistence, Azure configuration or speech-hook implementation changed. Existing uncommitted work was preserved. Nothing was committed, pushed or merged.

## Interview Room

- Replaced the stretched question/answer split with one continuous workspace: question, optional playback, response controls, editor and explicit Submit. Question typography leads; role, round, experience and progression mode are compact context.
- Submitted answers sit in a keyboard-accessible disclosure below the active task instead of competing with it.
- Voice states have distinct text: listening to the question, connecting the microphone, recording, processing final speech, transcript review and submitting. Text and Voice are ordinary pressed-state buttons with native keyboard operation, rather than incomplete ARIA tabs.
- While recording or finishing recognition, the transcript editor is read-only. Stop & Review remains separate from Submit. Final text is editable after draining recognition. Interim speech is never submitted by the UI.
- During review, Record More becomes secondary; Submit is the clear primary action. Question playback has replay/mute/stop, plus cancellation while audio is loading, wired to existing callbacks.
- Errors preserve the answer and offer Text fallback. An interview-load error can retry the same session.
- Progress no longer labels the current unanswered primary question as completed or claims the final question is 100% complete. It announces primary-question position and submitted response count separately from follow-ups.
- Draft copy explicitly says answers are temporary until submitted. Navigation, browser history and refresh are guarded while text, interim speech or microphone work is unsent. Ending an interview also warns first. Cancelling keeps the answer and session. Browser-native dialogs provide keyboard handling; refresh uses the browser's standard warning wording.
- The history dispatcher must register before BrowserRouter's listener. A browser regression caught that an effect-only listener could run after the router had already unmounted the workspace. The final dispatcher intercepts cancellation first, restores the previous history index without adding entries, and is inactive outside a guarded workspace. Keep this regression when upgrading React Router.
- Existing speech animations respect reduced-motion preferences in the focused room.

## Practice Workspace

- A question/editor column and an adjacent coaching column on wide screens replace the stack of nested cards. Tablet/mobile use a deliberate single-column reading order.
- The workflow is Question -> Answer -> Coaching -> Improved Attempt. Hints and the reference example are behind a native disclosure, with progressive hint controls and explicit assistance explanations.
- Both reference and coaching examples are labelled AI-generated possibilities, not authoritative benchmarks. Revealing a reference still requires the existing confirmation and preserves assistance tracking across retries.
- Coaching leads with the actual next action (or an available improvement suggestion), followed by a primary Improve my answer button. Missing points, concrete improvement suggestions and strengths follow. Answer structure, AI example and saved attempt comparison are progressively disclosed. Similar-question generation is secondary.
- Improve my answer focuses the editor and reuses the last answer when empty; it never silently clears existing edits. Successful coaching focuses its heading. Two saved attempts can be compared with their own assistance levels; no numeric improvement score is invented.
- Unavailable coaching stays explicitly unavailable. Submitted answers remain reviewable without fabricated praise, omissions or scores.
- Hint/reference/coaching/generation failures use contextual alerts, preserve edits and can be retried with the same action. A synchronous operation lock prevents overlapping requests and duplicate in-flight coaching submissions. Question selection is disabled during pending work.
- Saved questions use a labelled native select. Changing questions or generating a new one warns about unsubmitted edits. Empty sessions can generate their first question. Source-report session identifiers and interview tracks retain the Phase 1 navigation behavior, including refresh.

## Files changed in Phase 3

Production:

- `frontend/src/pages/InterviewRoom.tsx`
- `frontend/src/pages/InterviewWorkspace.css` (new, scoped to active room)
- `frontend/src/features/interview/AnswerBox.tsx`
- `frontend/src/features/interview/QuestionCard.tsx`
- `frontend/src/features/interview/ProgressBar.tsx`
- `frontend/src/pages/PracticeWorkspace.tsx`
- `frontend/src/pages/PracticeLearning.css` (new, scoped to active workspace)
- `frontend/src/features/practice/PracticeCoaching.tsx` (new)
- `frontend/src/hooks/useUnsentAnswerWarning.ts` (new)

Verification and documentation:

- `frontend/tests/phase3Workspaces.test.tsx` (new)
- `scripts/verify_ui_phase3.mjs` (new)
- `docs/ui-ux-phase3-workspaces.md` (this file)
- Ignored local artifacts in `storage/ui-phase3/`, including before/after images, a screenshot gallery and browser result JSON.

## Regression results

| Check | Result | Evidence and scope |
| --- | --- | --- |
| Complete frontend suite | PASS, 47 tests | Existing 39 plus 8 focused Phase 3 tests. Includes prior speech finalization, expiry, cleanup, stale playback and submission tests. |
| TypeScript/Vite production build | PASS | Existing large-chunk warning remains; no dependency added. |
| Responsive states | PASS | 320, 375, 768 and 1440 px. Populated, loading and error states on both pages; empty Practice session, completed interview and unavailable coaching. |
| Visible element bounds | PASS | Visible interactive element bounding boxes checked against viewport, along with document overflow and accessible form names. Every captured mock voice state checked at all four widths for Technical and HR. |
| Text interview | PASS, offline browser | Answer, one submission, follow-up, cleared editor; failed load retry and completion. |
| Voice workflow | PASS, mocked browser and deterministic tests | Playback -> connect -> record -> stop -> final segments -> editable review -> separate single submission -> next question -> Text. No microphone opened by mode transitions. |
| Rapid switching and permission recovery | PASS, mocked | Cancel connection, switch modes while draining speech, retain final words, release tracks, permission-denied Text recovery. |
| Unsent answer warnings | PASS | Cancelled route departure, End, refresh and browser-history departure preserve edits. No durable draft promise. |
| Practice assistance and coaching | PASS, offline browser | Progressive hints, reference confirmation, assisted retries, failed request recovery, focus, comparison and secondary similar-question action. |
| Report -> Practice -> Report | PASS, offline browser | HR track, source numeric report ID and session UUID retained, including refresh. |
| Keyboard | PASS for exercised flows | Native button activation, hint disclosure, reference dialog initial focus/containment, coaching/editor focus and native saved-question select. Not a full screen-reader audit. |
| Live Azure / physical microphone | NOT VERIFIED in this phase | No paid Azure calls. Speech SDK, media and audio are mocked in browser checks. Prior live acceptance is separate; final human microphone acceptance remains pending. |
| Backend tests | Not rerun | This phase changes only frontend presentation, navigation and client interaction guards. No backend/API/grading changes. |

Eight new deterministic tests cover router/refresh/history warnings, state-specific read-only transcript behavior, honest progress, progressive hints and source context, duplicate in-flight coaching/failure retry, coaching priority and saved comparison, and unavailable coaching.

Browser command from repository root: `node scripts/verify_ui_phase3.mjs`. It uses the existing temporary Playwright installation and installed Edge; it manages a native Vite server on port 5175 or accepts `PREPMATE_UI_BASE_URL`. API responses, recognition, microphone and audio playback are synthetic. No real account writes or paid speech requests are required. A Docker-forwarded frontend timeout was avoided by serving the same source through native Vite. One concurrent build/test attempt hit host memory exhaustion; sequential verification succeeded.

## Screenshots

[Full before/after gallery](../storage/ui-phase3/screenshots.md)

| Workspace | Desktop before | Desktop after | Mobile before | Mobile after |
| --- | --- | --- | --- | --- |
| Interview | [Before](../storage/ui-phase3/before-interview-1440.png) | [After](../storage/ui-phase3/after-interview-1440.png) | [Before](../storage/ui-phase3/before-interview-375.png) | [After](../storage/ui-phase3/after-interview-375.png) |
| Practice | [Before](../storage/ui-phase3/before-practice-1440.png) | [After](../storage/ui-phase3/after-practice-1440.png) | [Before](../storage/ui-phase3/before-practice-375.png) | [After](../storage/ui-phase3/after-practice-375.png) |

Before screenshots were captured from the preserved Phase 2 production bundle using the same representative fixture data. They were retained separately before building Phase 3. After screenshots are real browser captures of the updated frontend; voice screenshots show simulated states, not live speech evidence.

## Remaining limitations

- Final human microphone/listening acceptance is still outstanding. Physical iOS/Android behavior, Safari/Firefox and screen-reader reading order were not verified here.
- Unsubmitted drafts deliberately remain temporary. Browser warnings cannot protect against forced process termination or every mobile operating-system suspension. Standard refresh warnings depend on browser policy and user interaction.
- Source-report lookup retains the existing bounded 100-report fallback when a legacy URL lacks the source session UUID; unresolved origins link honestly to the Reports list. No API was added in this phase.
- AI coaching remains model-generated advice. Qualitative comparison is shown from saved attempts without inventing comparable numeric scores; assisted attempts stay labelled.
- The existing production bundle-size warning and legacy shared styles remain candidates for a separate maintenance pass. This phase uses scoped CSS rather than removing unrelated styles.
