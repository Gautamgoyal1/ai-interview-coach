> Historical iteration. The current theme follows the supplied [ink-and-amber specification](ink-and-amber-theme.md). The berry palette below is retained as previous design evidence.

# PrepMate ? Graphite Studio

17 November 2026. This refinement replaces the previous green, terracotta and brass
identity after visual review. It changes presentation only; the earlier uncommitted
implementation is preserved and source backups remain in local ignored evidence.

## Direction

A chalk-and-graphite interface with a muted berry accent. Navigation, dashboard,
setup, interview, reports, resume, practice, account and public pages use the same
surface family. Primary actions and selected states use one accent across pages,
including featured dashboard actions. Green, amber and red are reserved for actual
feedback/difficulty states, with existing text labels and numerical values retained.

Product screens use clear sans-serif headings; the editorial serif is limited to
brand marks and public/account storytelling. Large green panels and gold buttons
are removed. Paper and quiet neutral layers establish hierarchy without competing
brand colors. Both light and dark appearances follow the same color roles.

| Role | Light | Dark |
|---|---|---|
| Canvas | `#F6F5F3` | `#19191F` |
| Surface | `#FFFFFF` | `#222229` |
| Primary text | `#27262D` | `#F4F2F5` |
| Secondary text | `#55545E` | `#C6C2CB` |
| Primary accent | `#744457` | `#E2AFCA` |
| Primary hover | `#5F3548` | `#F0C7DD` |
| Selected fill | `#F3E9EE` | `#392D3B` |
| Sidebar | `#FCFBFD` | `#202027` |

## Color and motion contracts

`frontend/src/styles/tokens.css` remains the single source of application colors.
Material-specific names such as pine/olive/clay were replaced by neutral surface
and semantic role names. Normal button text, selection, navigation, focus, charts,
feedback and disabled states retain dedicated foreground/background pairs.

`frontend/src/styles/motion.css` adds short page fades, heading entrances and
menu/dialog reveals (160?280 ms), plus restrained button hover feedback. Whole
page containers do not retain transforms, preserving fixed overlay positioning.
Recording and transcript editing do not animate between voice states. Reduced
motion disables the new animations. No JavaScript animation dependency, timer,
state field or event handler was introduced.

## Preserved behavior

No changes to backend code, question generation, RAG, grading, scoring, reports,
speech hooks, authentication state, services or database data. The only changed
existing TSX file in this refinement is the profile's appearance-label copy.
All prior interview and practice handlers remain byte-for-byte unchanged.
The favicon uses the same accent as the application.

## Verification evidence

Local evidence is under `storage/ui-identity/refinement/` and is intentionally
ignored by Git. The current receipt is `verification.json`. Browser checks use
synthetic API responses and mocked microphone/audio/Speech SDK controls; no paid
provider calls or live database writes are part of this task. Real microphone or
human-listening acceptance is not claimed.

The browser initially failed using its default temporary profile. An isolated
workspace profile with GPU disabled passed the launch smoke check and was then
used for screenshots. The full frontend tools were invoked directly through Node
because this shell blocked npm.ps1 and npm.cmd was unreliable; the commands match
the package's Vitest, TypeScript and Vite scripts. Logs are preserved locally.

Screenshot comparisons use the preceding iteration as the baseline:

| View | Previous | Current |
|---|---|---|
| Dashboard | [Previous](../storage/ui-identity/final/dashboard-light-1440-viewport.png) | [Current](../storage/ui-identity/refinement/after/dashboard-light-1440-viewport.png) |
| Interview | [Previous](../storage/ui-identity/final/interview-dark-375-viewport.png) | [Current](../storage/ui-identity/refinement/after/interview-dark-375-viewport.png) |
| Setup | [Previous](../storage/ui-identity/final/setup-light-1440-viewport.png) | [Current](../storage/ui-identity/refinement/after/setup-light-1440-viewport.png) |
| Practice | [Previous](../storage/ui-identity/final/practice-dark-375-viewport.png) | [Current](../storage/ui-identity/refinement/after/practice-dark-375-viewport.png) |
| Landing | [Previous](../storage/ui-identity/final/landing-light-1440-viewport.png) | [Current](../storage/ui-identity/refinement/after/landing-light-1440-viewport.png) |

Screenshots are local review artifacts, not public downloads. Semantic contrast
checks and computed-text sampling are not complete WCAG certification. Safari,
Firefox, physical devices, screen-reader review and live Azure/microphone
acceptance remain outside this verification. The pre-existing bundle-size warning
remains; no dependency or bundle restructuring is included.

No commit, push, merge or deployment is performed.

## Final results

- 57 frontend tests passed in 7 files, including accent-consistency and contrast regressions.
- TypeScript and Vite production build passed. The existing ~748.49 kB main-chunk warning remains.
- 120 route/theme/viewport cases passed: 15 views at 320, 375, 768 and 1440px, light and dark.
- No final element-bound, document-overflow, unnamed-input, runtime-error or sampled-text contrast failures.
- 22 additional loading/empty/error/partial-state captures and 10 keyboard/validation/hover checks passed.
- Reduced-motion checks passed, including the new dashboard/heading animations being disabled.
- Eight mocked interview/practice interaction groups passed per theme, including final transcript review,
  explicit one-time submission, rapid switching, assistance tracking, retries and originating-report navigation.
- An initial rapid-switch assertion read the editor before its asynchronous render; the harness now waits
  for the rendered final transcript and retains the original value assertion. No speech implementation changed.
- Whitespace checks passed; no files are staged, committed or pushed.

The 120-case page matrix is one complete run; no earlier failing observations are
counted as passes. Interaction and state evidence are separate files. No paid AI
calls were made. Backend tests were not rerun because backend behavior and source
are unchanged.

## Files changed by this refinement

- `frontend/src/index.css`
- `frontend/src/components/Layout.css`
- `frontend/src/pages/Dashboard.css`
- `frontend/src/pages/History.css`
- `frontend/src/pages/InterviewWorkspace.css`
- `frontend/src/pages/Landing.css`
- `frontend/src/pages/Practice.css`
- `frontend/src/pages/PracticeLearning.css`
- `frontend/src/pages/Profile.css`
- `frontend/src/pages/Profile.tsx`
- `frontend/src/pages/Report.css`
- `frontend/src/pages/ResumeAnalysis.css`
- `frontend/src/styles/tokens.css`
- `frontend/src/features/interview/InterviewSetup.css`
- `frontend/src/styles/motion.css`
- `frontend/public/favicon.svg`
- `frontend/tests/designTokens.test.ts`
- `docs/visual-identity-redesign.md`
- `docs/theme-refinement.md`
