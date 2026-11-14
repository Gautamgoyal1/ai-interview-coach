# Azure Voice Interview Acceptance Report

Date: 14 November 2026 (Asia/Calcutta).

## Decision

Update: the two implementation bugs below have since been fixed and verified.
See [release blocker fixes](voice-release-blocker-fixes.md). This report retains
the original acceptance observations as the regression baseline. Physical
microphone and human listening results remain pending.

**NOT READY FOR BETA.** Real Azure STT/TTS and both automated interview journeys
worked, but mobile header controls are clipped and a Technical follow-up's
persisted evaluation was lost when advancing to the next primary question.
Physical microphone capture and human-audible playback remain NOT VERIFIED;
the user offered to run those checks but has not supplied results yet.

No application source, grading logic, schemas, or infrastructure configuration
was changed during this acceptance task. No push or merge was performed.

## Environment and method

- Docker Compose: backend, frontend, and PostgreSQL running; PostgreSQL healthy.
- Frontend login returned HTTP 200 and rendered without JavaScript errors.
- Backend served authenticated analysis/interview/speech requests successfully.
- Azure Speech key and endpoint configuration were present; region `eastasia`.
  No credentials or speech tokens were printed.
- Backend process inspection found one serving application worker, a reload
  supervisor, and its resource tracker. This is development `uvicorn --reload`,
  not a production deployment configuration.
- Microsoft Edge headless used a clean, isolated browser profile.
- A new synthetic acceptance account, synthetic resume analysis, and two interview
  sessions were created through the application APIs/UI. Existing users were not
  modified. Test records remain for investigation.
- Azure generated two WAV fixtures: Technical 79.48 seconds and HR 76.36 seconds.
  Edge's prerecorded test microphone fed those files through the actual browser
  Speech SDK to real Azure STT. Recording windows were approximately 83 and 80
  seconds, including trailing silence. This is **not a physical microphone test**.
- No Azure STT/TTS responses were mocked in these journeys. The TTS cancellation
  check deliberately delayed delivery of a real backend response to exercise the
  race. Silence and microphone-denial checks used browser test-device controls.
- Temporary authorization for recovery checks was deleted afterward. Test tools,
  audio, screenshots, and raw measurement JSON are in ignored
  `storage/voice-acceptance/`, without stored authentication tokens.

## PASS / FAIL / NOT VERIFIED matrix

| Requirement | Result | Evidence / limitation |
|---|---|---|
| Docker/services and backend availability | PASS | Compose status and successful real HTTP flows |
| Speech environment configured | PASS | Presence flags only; credentials not exposed |
| Single backend worker | PASS | Runtime process inspection |
| Azure token connectivity | PASS | Live issuance, 1,012 ms |
| Azure TTS connectivity | PASS | WAV fixture generation and app MP3 playback |
| Azure browser SDK STT connectivity | PASS | Real Azure recognition of both fixtures |
| Login | PASS | New acceptance user signed in through browser UI |
| Technical track and Voice Mode | PASS | Generated Technical question and active speech controls |
| Technical 60–90 second answer | PASS (prerecorded) | 79.48-second fixture; closing sentence captured |
| Technical transcript review/edit | PASS | Edited text persisted exactly |
| Technical single submission | PASS | Double-click produced one answer request and one saved turn |
| Technical next/contextual follow-up | PASS | Follow-up addressed missing supervised/unsupervised examples |
| Technical replay | PASS | Browser decoded audio and emitted `playing` |
| HR track and HR-specific question | PASS | Behavioral experience question generated |
| HR 60–90 second answer | PASS (prerecorded) | 76.36-second fixture; closing sentence captured |
| HR review/edit/single submission | PASS | Edited text persisted once despite double-click |
| HR contextual follow-up | PASS | Follow-up explicitly distinguished team-conflict answer from requested ML-project evidence |
| HR replay | PASS | Browser decoded audio and emitted `playing` |
| Existing HR rubric path | PASS | Persisted reasoning, trade-offs, communication, relevance, and reflection dimensions |
| Voice appropriateness and human audibility | NOT VERIFIED | Default voices are Jenny/Aria; no human listening observation |
| Physical microphone and human speech | NOT VERIFIED | User results pending; automated input was prerecorded |
| Final words retained | PASS (prerecorded) | Exact closing sentence appeared in both transcripts |
| Microphone permission denial | PASS | Browser denied microphone; controlled error and editable Text fallback |
| Silence | PASS | Empty transcript, submission disabled, zero active tracks after Stop |
| Rapid Start/Stop and Voice/Text switching | PASS | Returned to review with zero active tracks |
| Interrupted recording/network loss | PASS | Review/error recovered and tracks released after 15,226 ms |
| Voice-to-Text fallback submission | PASS | Typed answer accepted and persisted |
| Refresh saved progress | PASS | Saved answer and current question restored |
| Refresh during recording | PASS with limitation | New document had no active tracks; physical hardware indicator not observed |
| Pending TTS cancellation | PASS | No playback after switching to Text with delayed real TTS response |
| Desktop 1440 px | PASS | Screenshot inspected; header controls inside viewport |
| Tablet 768 px | PASS | Screenshot inspected; header controls inside viewport |
| Mobile 375 px | FAIL | Main content fits, but Dashboard/End interview are outside viewport |
| Persisted grading on next-primary transition | FAIL | Grading completed in graph history but saved turn evaluation was NULL |
| Real devices, other browsers, autoplay policy defaults | NOT VERIFIED | Edge headless used an explicit autoplay allowance |
| Long-session token renewal with real Azure | NOT VERIFIED | Not exercised for nine minutes in this acceptance run |

## Actual performance measurements

These are representative single-run measurements, not percentiles or guarantees.
Browser TTS response-header timings include application and network time; they
cannot isolate Azure generation time. The separate complete-fetch sample includes
response-body transfer. Instrumentation and browser click overhead are included
in user-action timings.

| Measurement | Technical | HR |
|---|---:|---:|
| Initial app TTS response headers | 1,118 ms | 1,334 ms |
| Replay app TTS response headers | 1,439 ms | 1,417 ms |
| Start click to Listening | 2,433 ms | 2,500 ms |
| Listening to first finalized segment | 6,527 ms | 6,252 ms |
| Stop click to Transcript Review | 252 ms | 238 ms |
| Submit edited answer to next/follow-up response | 6,175 ms | 6,326 ms |

Additional measurements:

- Direct Azure TTS fixture generation: Technical 6,939 ms; HR 6,715 ms.
- Complete app TTS fetch sample: 1,368 ms.
- Fetch completion to browser `playing`: 56 ms.
- Request start to browser `playing`: 1,424 ms.
- Network-loss stop/review recovery: 15,226 ms; zero active microphone tracks.

## Transcript observations

Word error rate used lowercase alphanumeric word tokens and Levenshtein edit
 distance, ignoring punctuation. It is only an observation on clean, synthesized
English audio; it does not predict accuracy with accents, noise, physical devices,
or spontaneous speech.

| Sample | Reference tokens | Recognized tokens | Word error rate | Final sentence |
|---|---:|---:|---:|---|
| Technical | 182 | 183 | 1.10% | Present |
| HR | 186 | 186 | 0.54% | Present |

Technical recognition changed "evaluation metrics" to "a valuation metrics".
HR recognition rendered "one focused question" as "1 focused question"; the
normalization counts that as a word substitution. Both transcripts ended with
"That is the final sentence of my answer." Editing was available before submit.

## Remaining bugs and limitations

### High priority: evaluation lost on progression

The Technical follow-up `q_001_fu_1` was answered via Text fallback and advanced
successfully to primary question two. Its `interview_turns.evaluation` was NULL,
while `graph_state.evaluation_history` contained its completed `v1.0` grade.

`generate_question` clears `current_evaluation` in
`backend/app/modules/interview/nodes.py:290`. The service subsequently persists
`updated_state.get("current_evaluation")` in
`backend/app/modules/interview/service.py:389`. This explains the observed loss
when an answer advances to the next primary question. Reports aggregate saved
turn evaluations, so this can reduce grading coverage. No grading code was
changed during this acceptance task; the issue is in the existing flow.

Evidence:
`storage/voice-acceptance/grading-persistence-confirmation.json` and
`grading-persistence-investigation.json`.

### Mobile: header actions outside viewport

At width 375, Dashboard spans x=373–490 and End interview spans x=502–639.
Both remain CSS-visible in the DOM but are clipped outside the usable viewport.
A simple `isVisible()` or document-overflow test gave a false pass; bounding-box
inspection and screenshots confirmed the failure. At 768 and 1440 both controls
are inside the viewport.

Evidence: `storage/voice-acceptance/layout-report.json` and
`header-controls-375.png`.

### Test-harness correction

The first permission-denial attempt used an unsupported CDP permission name,
`audioCapture`, and failed before exercising the product. The corrected
`microphone` descriptor passed. The raw recovery JSON retains the harness error;
`permission-report.json` is the final product result. Likewise, the initial
mobile visibility pass is superseded by `layout-report.json`.

### Remaining manual gate

At `http://localhost:5173`, sign in normally and run Technical, then HR Voice Mode:

1. Listen to a complete question without changing browser autoplay defaults.
2. Speak for 60–90 seconds and end with "That is the final sentence of my answer."
3. Stop, wait for Transcript Review, and confirm the closing sentence and earlier
   segments. Note missing words and the measured delay after Stop.
4. Edit the transcript and submit. Confirm exactly one saved answer and a relevant
   next question/follow-up, then replay it.
5. Deny permission and verify Text fallback; try noise, silence, a short network
   interruption, rapid switching, and a refresh on actual devices.
6. Report Technical and HR separately, including browser/device, audible playback,
   final sentence, edit/save result, and any errors.

Beta should wait for the two confirmed bugs to be addressed and this manual gate
completed. The acceptance run did not rerun the earlier 250 backend / 26 frontend
unit and integration checks; those results belong to the stabilization task.

## Evidence links

- [Desktop Technical review](../storage/voice-acceptance/technical-transcript-review-desktop.png)
- [Desktop HR review](../storage/voice-acceptance/hr-transcript-review-desktop.png)
- [Tablet interview](../storage/voice-acceptance/technical-room-768.png)
- [Mobile interview](../storage/voice-acceptance/technical-room-375.png)
- [Mobile header control failure](../storage/voice-acceptance/header-controls-375.png)
- [Browser journey results](../storage/voice-acceptance/browser-report.json)
- [Recovery results](../storage/voice-acceptance/recovery-report.json)
- [Corrected permission result](../storage/voice-acceptance/permission-report.json)
- [Layout results](../storage/voice-acceptance/layout-report.json)
