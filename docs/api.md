# API overview

The running backend exposes its canonical OpenAPI schema at `/openapi.json` and interactive documentation at `/docs`. Paths below have no `/api` prefix. This overview is generated from the current app routes; it does not make external provider requests.

## Authentication and flow

Register/login under `/auth`; protected routes use `Authorization: Bearer <access-token>`. Start with a saved resume analysis ID, then start an interview and submit the current question ID with an answer. Reports identify the interview session; practice can retain its originating report/track. Request/response schemas and status codes are available in OpenAPI.

Generation unavailability can return controlled 503 after an answer was saved. Fetch the session and use its explicit retry endpoint rather than resubmitting the old answer. Ownership checks apply to saved resources. Speech endpoints require authentication and never return the subscription key.

## Routes

| Method | Path | Summary |
|---|---|---|
| POST | `/auth/change-password` | Change Password |
| POST | `/auth/login` | Login |
| GET | `/auth/me` | Get Me |
| PATCH | `/auth/profile` | Update Profile |
| POST | `/auth/register` | Register |
| GET | `/health` | Health |
| POST | `/interview/start` | Start Interview |
| GET | `/interview/{session_id}` | Get Interview Session |
| DELETE | `/interview/{session_id}` | Delete Interview Session |
| POST | `/interview/{session_id}/answer` | Submit Interview Answer |
| POST | `/interview/{session_id}/end` | End Interview Session |
| POST | `/interview/{session_id}/retry-question` | Retry Question |
| POST | `/practice/questions/{question_id}/attempts` | Submit Practice Attempt |
| GET | `/practice/questions/{question_id}/attempts` | List Question Attempts |
| POST | `/practice/questions/{question_id}/hints/{level}/reveal` | Reveal Hint |
| POST | `/practice/questions/{question_id}/reference/reveal` | Reveal Reference Answer |
| GET | `/practice/recommendations` | Get Practice Recommendations |
| POST | `/practice/sessions` | Create Practice Session |
| GET | `/practice/sessions` | List Practice Sessions |
| GET | `/practice/sessions/{session_id}` | Get Practice Session |
| DELETE | `/practice/sessions/{session_id}` | Delete Practice Session |
| POST | `/practice/sessions/{session_id}/questions` | Generate Next Question |
| GET | `/reports` | List Interview Reports |
| GET | `/reports/interviews/{session_id}` | Get Interview Report |
| DELETE | `/reports/interviews/{session_id}` | Delete Interview Report |
| POST | `/reports/interviews/{session_id}/generate` | Generate Interview Report |
| GET | `/resume/analyses` | List Resume Analyses |
| GET | `/resume/analyses/{analysis_id}` | Get Resume Analysis |
| DELETE | `/resume/analyses/{analysis_id}` | Delete Resume Analysis |
| POST | `/resume/analyze` | Analyze Resume |
| POST | `/speech/synthesize` | Synthesize text to speech using Azure Neural TTS |
| GET | `/speech/token` | Get short-lived Azure Speech authorization token (GET) |
| POST | `/speech/token` | Get short-lived Azure Speech authorization token |
| GET | `/speech/voices` | List available calibrated Azure Neural voices |

## Verification scope

`GET /health` confirms the process is serving. It is not an Azure/Gemini/database readiness certification. The README documents the single-worker development constraint and optional Speech setup. Do not place provider keys in request examples or frontend environment variables.
