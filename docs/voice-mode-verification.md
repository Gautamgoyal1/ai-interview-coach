# Azure Voice Mode verification

Voice answers use a two-step flow: **Stop & Review Transcript**, followed by an
explicit **Submit answer**. Only finalized recognition segments enter the answer.
Interim text is a preview. A failed or timed-out stop retains captured text and
asks the candidate to review and add missing words; it never submits automatically.

## Automated checks

- Backend: from `backend`, run `..\.venv\Scripts\python.exe -m pytest tests -q`.
- Frontend: from `frontend`, run `npm test` and `npm run build`.
- Speech tests use isolated users and mock Azure. They never call paid endpoints.

## Controlled browser acceptance test

Real Azure checks with prerecorded microphone input have been performed. See
[the acceptance report](voice-mode-acceptance-report.md) for results, measured
timings, screenshots, and two remaining bugs. Physical microphone and human
listening checks remain pending; the steps below are still the manual gate.

The two implementation bugs are now fixed; see
[release blocker verification](voice-release-blocker-fixes.md) for PostgreSQL
regressions and mobile header checks.

Use HTTPS or localhost, a supported microphone, and a configured backend speech
resource. Never place the subscription key in frontend configuration.

For both Technical and HR interviews:

1. Select Voice Mode and start an interview. Verify the question plays once.
2. Record a 60–90 second answer. End with a distinctive final sentence, then stop.
3. Wait for Transcript Review. Verify the final sentence and earlier segments are
   present, and that interim preview text was not submitted.
4. Edit the transcript. Submit once, including an attempted rapid double click.
   Verify one answer is saved and the next question appears and plays.
5. Replay, stop, and mute question audio. Start recording during pending synthesis;
   verify question audio cannot play over the microphone.
6. Switch rapidly between Text and Voice while connecting and while recording.
   Verify finalized text is retained, controls recover, and only one mic is active.
7. Deny mic permission, disconnect the network, and retry. Verify a useful error,
   released microphone indicators, editable captured text, and Text Mode fallback.
8. Record through a token renewal (approximately nine minutes); verify continued
   transcription. Interrupt renewal and verify capture ends with a review message.
9. Navigate away during recording or synthesis. Verify no later audio plays and
   the microphone indicator turns off. Refresh an interview and verify saved
   progress returns. Unsubmitted drafts/audio state are not persisted.

## Deployment constraints

- Use **one backend worker**: graph checkpoints, interview locks, and speech rate
  limits remain process-local. Restarts reset speech limits and token caches.
- Speech token issuance allows 30 requests/user/minute; synthesis allows 20.
  Azure authorization tokens are resource-scoped bearer capabilities. These
  endpoint limits do not cap direct Azure SDK consumption after issuance; apply
  resource quotas/budgets before a broader rollout.
- Aborting synthesis stops browser playback and cancels the browser request.
  A request already delivered to Azure may still complete and incur a charge.
- Verify real Azure behavior and target browser autoplay policies before rollout.
