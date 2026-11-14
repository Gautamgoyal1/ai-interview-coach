import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { chromium } from "../storage/voice-acceptance/node_modules/playwright/index.mjs";
import { mkdir, writeFile } from "node:fs/promises";
const dir = "storage/ui-phase3";
const baseURL = process.env.PREPMATE_UI_BASE_URL || "http://127.0.0.1:5175";
await mkdir(dir, { recursive: true });
const failed = new Set();
const requests = {};
const creates = [];
const passed = [];
function pass(name) {
  passed.push(name);
  console.log(JSON.stringify({ check: name, status: "PASS" }));
}
const date = "2026-11-14T09:30:00Z";
const user = {
  id: 1,
  email: "alex@example.com",
  full_name: "Alex Morgan",
  target_role: "Machine Learning Engineer",
  experience_level: "fresher",
  created_at: date,
};
const analysis = {
  id: 1,
  filename: "Alex_Morgan_ML_Resume.pdf",
  job_role: user.target_role,
  created_at: date,
  match_score: 72,
  version: 2,
  interview_count: 3,
};
const result = {
  analysis_id: 1,
  version: 2,
  job_role: user.target_role,
  resume_skills: ["Python", "pandas", "machine learning", "SQL"],
  matched_skills: ["Python", "pandas", "machine learning"],
  missing_skills: ["Docker", "model evaluation", "cloud platforms"],
  match_score: 72,
  skill_evidence: { Python: "demonstrated", pandas: "mentioned_only" },
  strengths: [
    "Built a Python pipeline to clean and validate tabular datasets.",
    "Explains model selection using project context.",
  ],
  improvement_suggestions: [
    "Add precision and recall results to your model evaluation project.",
    "Show a deployment example with Docker.",
    "Quantify the business impact of your feature engineering choices.",
  ],
  likely_interview_questions: [
    "How would you handle data leakage in a training pipeline?",
  ],
};
const rec = {
  topic: "Model evaluation",
  interview_type: "technical",
  target_role: user.target_role,
  observed_gap: "Accuracy alone concealed poor minority-class recall.",
  suggested_action: "Practice selecting metrics for imbalanced data.",
  source_report_id: 1,
  priority: "high",
};
const reportSummary = {
  id: 1,
  session_id: "audit-interview",
  target_role: user.target_role,
  interview_type: "technical",
  interview_date: date,
  status: "completed",
  overall_score: 68,
  rubric_version: "v1.0",
  created_at: date,
};
const dimNames = {
  technical_correctness: "Technical Correctness",
  relevance: "Relevance",
  completeness: "Completeness",
  technical_depth: "Technical Depth",
};
const dimensions = Object.fromEntries(
  Object.entries(dimNames).map(([key, label], i) => [
    key,
    {
      dimension: key,
      label,
      weight: [0.4, 0.2, 0.25, 0.15][i],
      average_score: [3.5, 4, 3, 2.8][i],
      percentage: [70, 80, 60, 56][i],
      evaluated_count: 4,
    },
  ]),
);
const feedback = {
  question_id: "q_001",
  question_index: 1,
  is_follow_up: false,
  parent_question_id: null,
  topic: "Model evaluation",
  difficulty: "medium",
  question_text: "How would you evaluate an imbalanced classification model?",
  answer_text:
    "I would compare precision and recall, inspect the confusion matrix, and choose the threshold based on the cost of false negatives.",
  overall_score: 68,
  grading_status: "completed",
  dimension_scores: Object.fromEntries(
    Object.keys(dimNames).map((key) => [
      key,
      {
        score: 3.4,
        explanation:
          "Clear metric selection, but the threshold trade-off needs a concrete example.",
      },
    ]),
  ),
  strengths: ["Connects precision and recall to error costs."],
  missing_concepts: ["Threshold calibration"],
  improvement_suggestions: [
    "Explain how you choose a threshold using validation data.",
  ],
};
const report = {
  ...reportSummary,
  dimension_scores: dimensions,
  topic_scores: [
    {
      topic: "Model evaluation",
      score: 68,
      questions_asked: 3,
      evaluated_questions: 3,
    },
    { topic: "Python", score: 82, questions_asked: 1, evaluated_questions: 1 },
  ],
  strengths: ["Clear explanation of precision and recall."],
  weaknesses: ["Threshold selection lacked a concrete trade-off."],
  missing_concepts: ["Threshold calibration"],
  recommendations: [
    {
      area: "Model evaluation",
      observed_gap: rec.observed_gap,
      action: rec.suggested_action,
      priority: "high",
    },
  ],
  question_feedback: [feedback],
  completion_stats: {
    questions_answered: 4,
    primary_questions_completed: 3,
    follow_ups_answered: 1,
    total_primary_questions: 3,
  },
  evaluation_coverage: {
    evaluated_count: 4,
    unavailable_count: 0,
    total_answered: 4,
    coverage_ratio: 1,
    is_partial: false,
  },
  rubric_weights: {
    technical_correctness: 0.4,
    relevance: 0.2,
    completeness: 0.25,
    technical_depth: 0.15,
  },
  error_message: null,
  updated_at: date,
};
const coach = {
  correct_points: ["Correctly identifies precision and recall."],
  missing_points: ["Threshold selection example"],
  improvement_suggestions: [
    "State the relative cost of false positives and negatives.",
  ],
  suggested_structure: [
    "Define the objective",
    "Choose metrics",
    "Discuss threshold trade-offs",
  ],
  improved_example_answer:
    "I would measure precision and recall on held-out data, then choose a threshold based on the cost of missed positives. For fraud detection, I might prioritize recall while monitoring false-positive review costs.",
  next_action: "Retry with a concrete threshold example.",
  evaluation_status: "completed",
  evaluation_confidence: "high",
  improvements_from_previous: [],
};
const practice = {
  id: "audit-practice",
  user_id: 1,
  interview_type: "technical",
  target_role: user.target_role,
  topic: "Model evaluation",
  source_report_id: 1,
  experience_level: "fresher",
  weakness_context: rec.observed_gap,
  status: "active",
  created_at: date,
  updated_at: date,
  questions: [
    {
      id: "practice-q1",
      session_id: "audit-practice",
      question_text:
        "When would accuracy be misleading, and which metrics would you use instead?",
      topic: "Model evaluation",
      difficulty: "medium",
      hints_revealed: [1],
      revealed_hints: {
        1: "Consider what happens when one class represents only one percent of examples.",
      },
      reference_revealed: false,
      reference_answer: null,
      reference_explanation: null,
      created_at: date,
      attempts: [
        {
          id: "attempt1",
          question_id: "practice-q1",
          attempt_number: 1,
          answer_text: feedback.answer_text,
          assistance_level: "hint_assisted",
          hints_used: [1],
          reference_revealed: false,
          feedback: coach,
          created_at: date,
        },
      ],
    },
  ],
};
const interview = {
  session_id: "audit-interview",
  analysis_id: 1,
  target_role: user.target_role,
  interview_type: "technical",
  experience_level: "fresher",
  starting_difficulty: "medium",
  progression_mode: "adaptive",
  status: "in_progress",
  question_index: 2,
  max_questions: 8,
  follow_up_count: 0,
  max_follow_ups: 1,
  current_question: {
    question_id: "q_002",
    topic: "Model evaluation",
    difficulty: "medium",
    question_text: feedback.question_text,
    question_type: "applied",
    is_follow_up: false,
  },
  conversation_history: [{ ...feedback, created_at: date, answered_at: date }],
  started_at: date,
  completed_at: null,
};
let scenario = "populated";
let allowDialog = true;
const dialogs = [];
const answerBodies = [];
const practiceBodies = [];
const originalPractice = structuredClone(practice);
const resetPractice = () => {
  Object.assign(practice, structuredClone(originalPractice));
};
const fakeSDK = `export const SpeechConfig={fromAuthorizationToken:()=>({})};
export const AudioConfig={fromStreamInput:()=>({close(){}})};
export const ResultReason={RecognizedSpeech:3};
export class SpeechRecognizer {
 constructor(){window.mockRecognizers.push(this);}
 startContinuousRecognitionAsync(ok){this.begin=ok;}
 stopContinuousRecognitionAsync(ok){this.finish=ok;}
 close(){this.closed=true;}
}
export default {SpeechConfig,AudioConfig,ResultReason,SpeechRecognizer};`;
let devServer;
if (!process.env.PREPMATE_UI_BASE_URL) {
  devServer = spawn(
    process.execPath,
    [
      "node_modules/vite/bin/vite.js",
      "--host",
      "127.0.0.1",
      "--port",
      "5175",
      "--strictPort",
    ],
    { cwd: "frontend", stdio: "ignore", windowsHide: true },
  );
  process.on("exit", () => devServer?.kill());
  let ready = false;
  for (let i = 0; i < 50; i++) {
    try {
      const response = await fetch(baseURL);
      if (response.ok) {
        ready = true;
        break;
      }
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  assert(ready, "Local Vite server did not start");
}
const browser = await chromium.launch({
  executablePath:
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  headless: true,
});
const observations = [];
try {
  const context = await browser.newContext();
  await context.addInitScript(() => {
    localStorage.setItem("access_token", "offline-design-audit");
    localStorage.setItem("theme", "light");
  });
  await context.addInitScript(() => {
    window.mockRecognizers = [];
    window.mockPlayers = [];
    window.micCalls = 0;
    window.closedTracks = 0;
    window.denyMic = false;
    Object.defineProperty(navigator.mediaDevices, "getUserMedia", {
      value: async () => {
        window.micCalls++;
        if (window.denyMic)
          throw new DOMException("Permission denied", "NotAllowedError");
        return { getTracks: () => [{ stop: () => window.closedTracks++ }] };
      },
    });
    window.Audio = class {
      constructor() {
        window.mockPlayers.push(this);
      }
      async play() {
        this.onplay?.();
      }
      pause() {
        this.paused = true;
      }
      removeAttribute() {}
      load() {}
    };
  });
  const page = await context.newPage();
  page.on("dialog", async (dialog) => {
    dialogs.push({ type: dialog.type(), message: dialog.message() });
    if (allowDialog) await dialog.accept();
    else await dialog.dismiss();
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.includes("/deps/microsoft-cognitiveservices-speech-sdk"))
      return route.fulfill({
        contentType: "application/javascript",
        body: fakeSDK,
      });
    if (!["localhost", "127.0.0.1"].includes(url.hostname))
      return route.fulfill({ status: 200, body: "" });
    if (url.port !== "8000") return route.continue();
    const p = url.pathname;
    requests[p] = (requests[p] || 0) + 1;
    if (failed.has(p))
      return route.fulfill({
        status: 503,
        json: { detail: "Simulated temporary failure" },
      });
    if (p === "/practice/sessions" && route.request().method() === "POST") {
      const payload = route.request().postDataJSON();
      creates.push(payload);
      practice.interview_type = payload.interview_type;
      practice.source_report_id = payload.source_report_id ?? null;
      practice.target_role = payload.target_role || user.target_role;
      return route.fulfill({ json: practice });
    }
    if (p === "/auth/me") return route.fulfill({ json: user });
    if (scenario === "loading") await new Promise((r) => setTimeout(r, 8000));
    if (scenario === "error")
      return route.fulfill({
        status: 503,
        json: {
          detail: "The service is temporarily unavailable. Please try again.",
        },
      });
    const empty = scenario === "empty";
    if (p === "/speech/token")
      return route.fulfill({
        json: { token: "offline-fixture", region: "fixture", expires_in: 600 },
      });
    if (p === "/speech/synthesize")
      return route.fulfill({
        contentType: "audio/mpeg",
        body: Buffer.from("offline simulated audio"),
      });
    if (p.match(/\/practice\/questions\/[^/]+\/hints\/([12])\/reveal$/)) {
      const level = Number(p.split("/").at(-2));
      const q = practice.questions.find((q) => p.includes(q.id));
      q.hints_revealed = [...new Set([...q.hints_revealed, level])];
      q.revealed_hints[String(level)] =
        level === 1
          ? "Consider class imbalance."
          : "Connect the chosen threshold to error costs.";
      return route.fulfill({
        json: {
          question_id: q.id,
          hint_text: q.revealed_hints[String(level)],
          hints_revealed: q.hints_revealed,
          assistance_level: "hint_assisted",
        },
      });
    }
    if (p.endsWith("/reference/reveal")) {
      const q = practice.questions.find((q) => p.includes(q.id));
      q.reference_revealed = true;
      q.reference_answer = "One possible explanation using validation data.";
      q.reference_explanation = "Adapt the example to your experience.";
      return route.fulfill({
        json: {
          question_id: q.id,
          reference_answer: q.reference_answer,
          reference_explanation: q.reference_explanation,
          reference_revealed: true,
          assistance_level: "reference_assisted",
        },
      });
    }
    if (p.endsWith("/attempts") && route.request().method() === "POST") {
      const q = practice.questions.find((q) => p.includes(q.id));
      const body = route.request().postDataJSON();
      practiceBodies.push(body);
      const attempt = {
        id: "attempt" + (q.attempts.length + 1),
        question_id: q.id,
        attempt_number: q.attempts.length + 1,
        answer_text: body.answer_text,
        assistance_level: q.reference_revealed
          ? "reference_assisted"
          : q.hints_revealed.length
            ? "hint_assisted"
            : "independent",
        hints_used: q.hints_revealed,
        reference_revealed: q.reference_revealed,
        feedback: {
          ...coach,
          improvements_from_previous: q.attempts.length
            ? ["Now explains threshold costs."]
            : [],
        },
        created_at: date,
      };
      q.attempts.push(attempt);
      await new Promise((r) => setTimeout(r, 350));
      return route.fulfill({ json: attempt });
    }
    if (p.endsWith("/questions") && route.request().method() === "POST") {
      const q = {
        ...structuredClone(originalPractice.questions[0]),
        id: "practice-q" + (practice.questions.length + 1),
        question_text: "How would you choose a decision threshold?",
        hints_revealed: [],
        revealed_hints: {},
        attempts: [],
      };
      practice.questions.push(q);
      return route.fulfill({ json: q });
    }
    if (p.endsWith("/answer") && route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      answerBodies.push(body);
      await new Promise((r) => setTimeout(r, 350));
      return route.fulfill({
        json: {
          ...interview,
          interview_type: p.includes("audit-hr") ? "hr" : "technical",
          question_index: 3,
          current_question: {
            ...interview.current_question,
            question_id: "q_003",
            is_follow_up: true,
            question_text:
              "How would you choose a threshold for this scenario?",
          },
        },
      });
    }
    if (p.endsWith("/end") && route.request().method() === "POST")
      return route.fulfill({
        json: { ...interview, status: "completed", current_question: null },
      });
    if (p === "/resume/analyses")
      return route.fulfill({
        json: empty
          ? []
          : [
              analysis,
              {
                ...analysis,
                id: 2,
                job_role: "Data Scientist",
                match_score: 61,
                filename: "Alex_Data_Science.pdf",
              },
            ],
      });
    if (p === "/resume/analyses/1")
      return route.fulfill({ json: { ...analysis, result } });
    if (p === "/resume/analyze")
      return route.fulfill({ json: { ...result, reused: true } });
    if (p === "/reports")
      return route.fulfill({
        json: empty
          ? []
          : [
              reportSummary,
              {
                ...reportSummary,
                id: 2,
                session_id: "audit-hr",
                interview_type: "hr",
                overall_score: 74,
              },
            ],
      });
    if (p.startsWith("/reports/interviews/"))
      return route.fulfill({
        json:
          scenario === "partial"
            ? {
                ...report,
                status: "partial",
                evaluation_coverage: {
                  ...report.evaluation_coverage,
                  is_partial: true,
                  unavailable_count: 2,
                  evaluated_count: 2,
                  coverage_ratio: 0.5,
                },
              }
            : report,
      });
    if (p === "/practice/recommendations")
      return route.fulfill({
        json: empty
          ? []
          : [
              rec,
              {
                ...rec,
                topic: "Stakeholder communication",
                interview_type: "hr",
                observed_gap: "Decision rationale needs clearer structure.",
              },
            ],
      });
    if (p === "/practice/sessions")
      return route.fulfill({
        json: empty
          ? []
          : [
              {
                ...practice,
                question_count: 1,
                attempt_count: 1,
                latest_attempt_at: date,
              },
            ],
      });
    if (p.startsWith("/practice/sessions/"))
      return route.fulfill({
        json: empty ? { ...practice, questions: [] } : practice,
      });
    if (p.startsWith("/interview/"))
      return route.fulfill({
        json: {
          ...interview,
          interview_type: p.includes("audit-hr") ? "hr" : "technical",
          current_question: p.includes("audit-hr")
            ? {
                ...interview.current_question,
                question_text:
                  "Tell me about a time you resolved a disagreement in a project team.",
              }
            : interview.current_question,
        },
      });
    if (p.startsWith("/speech/"))
      return route.fulfill({
        status: 503,
        json: { detail: "Speech service unavailable in offline design audit." },
      });
    return route.fulfill({ json: [] });
  });
  async function captureVoiceState(name) {
    for (const width of [320, 375, 768, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      const outside = await page
        .locator("main button,main a,main textarea,main summary")
        .evaluateAll((es) =>
          es
            .filter(
              (e) =>
                e.getClientRects().length &&
                getComputedStyle(e).visibility === "visible",
            )
            .map((e) => {
              const r = e.getBoundingClientRect();
              return { label: e.textContent, left: r.left, right: r.right };
            })
            .filter((r) => r.left < -1 || r.right > innerWidth + 1),
        );
      assert.deepEqual(outside, [], JSON.stringify({ name, width, outside }));
      assert(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      );
      await page.screenshot({
        path: `${dir}/${name}-${width}.png`,
        fullPage: true,
      });
    }
    await page.setViewportSize({ width: 375, height: 1000 });
  }
  async function capture(name, route, width = 1440, mode = "populated") {
    scenario = mode;
    errors.length = 0;
    await page.setViewportSize({ width, height: 1000 });
    await page.goto(baseURL + route, {
      waitUntil: "domcontentloaded",
    });
    await page.waitForTimeout(mode === "loading" ? 350 : 750);
    if (name === "landing") {
      for (
        let y = 0;
        y < (await page.locator("body").evaluate((e) => e.scrollHeight));
        y += 700
      ) {
        await page.evaluate((y) => scrollTo(0, y), y);
        await page.waitForTimeout(60);
      }
      await page.evaluate(() => scrollTo(0, 0));
      await page.waitForTimeout(400);
    }
    const outside = await page
      .locator("main button,main a,main input,main textarea,main select")
      .evaluateAll((es) =>
        es
          .filter(
            (e) =>
              e.getClientRects().length &&
              getComputedStyle(e).visibility === "visible",
          )
          .map((e) => {
            const r = e.getBoundingClientRect();
            return {
              tag: e.tagName,
              label:
                e.getAttribute("aria-label") || e.textContent?.slice(0, 50),
              left: r.left,
              right: r.right,
            };
          })
          .filter((r) => r.left < -1 || r.right > innerWidth + 1),
      );

    assert.deepEqual(outside, [], JSON.stringify({ name, width, outside }));
    await page.screenshot({
      path: `${dir}/${name}-${width}.png`,
      fullPage: true,
    });
    await page.screenshot({ path: `${dir}/${name}-${width}-viewport.png` });
    const stats = await page.evaluate(() => ({
      height: document.documentElement.scrollHeight,
      overflow: document.documentElement.scrollWidth > innerWidth,
      headings: [...document.querySelectorAll("h1,h2,h3")].map((e) =>
        e.textContent.trim(),
      ),
      unnamedInputs: [
        ...document.querySelectorAll(
          "input:not([type=hidden]),textarea,select",
        ),
      ]
        .filter(
          (e) =>
            !e.labels?.length &&
            !e.getAttribute("aria-label") &&
            !e.getAttribute("aria-labelledby"),
        )
        .map((e) => ({
          tag: e.tagName,
          id: e.id,
          placeholder: e.getAttribute("placeholder"),
        })),
      text: document.body.innerText.slice(0, 14000),
    }));
    assert.equal(stats.overflow, false, name);
    assert.deepEqual(stats.unnamedInputs, [], name);
    assert.deepEqual(errors, [], name);
    observations.push({ name, width, mode, errors: [...errors], ...stats });
    console.log(
      JSON.stringify({
        name,
        width,
        mode,
        height: stats.height,
        overflow: stats.overflow,
        errors,
      }),
    );
  }

  for (const width of process.env.PREPMATE_SKIP_MATRIX
    ? []
    : [320, 375, 768, 1440]) {
    resetPractice();
    await capture(
      "after-interview",
      "/interview/audit-interview?mode=text",
      width,
    );
    await capture(
      "after-practice",
      "/practice/audit-practice?reportId=1&reportSessionId=audit-interview",
      width,
    );
    await capture(
      "interview-loading",
      "/interview/audit-interview?mode=text",
      width,
      "loading",
    );
    await capture(
      "interview-error",
      "/interview/audit-interview?mode=text",
      width,
      "error",
    );
    await capture(
      "practice-loading",
      "/practice/audit-practice",
      width,
      "loading",
    );
    await capture("practice-error", "/practice/audit-practice", width, "error");
    await capture("practice-empty", "/practice/audit-practice", width, "empty");
  }
  if (!process.env.PREPMATE_SKIP_MATRIX)
    pass(
      "Responsive populated/loading/error/empty workspaces at all four widths: element bounds, labels, runtime errors",
    );
  scenario = "populated";
  await page.setViewportSize({ width: 375, height: 1000 });
  await page.goto(baseURL + "/interview/audit-interview?mode=text");
  await page
    .getByLabel("Your answer", { exact: true })
    .fill("An unsent answer with an example.");
  allowDialog = false;
  await page.getByRole("link", { name: "Dashboard", exact: true }).click();
  assert(page.url().includes("/interview/"));
  assert.equal(
    await page.getByLabel("Your answer", { exact: true }).inputValue(),
    "An unsent answer with an example.",
  );
  await page
    .getByRole("button", { name: "End interview", exact: true })
    .click();
  assert.equal(requests["/interview/audit-interview/end"] || 0, 0);
  await page.reload({ timeout: 2000 }).catch(() => {});
  assert.equal(
    await page.getByLabel("Your answer", { exact: true }).inputValue(),
    "An unsent answer with an example.",
  );
  await page.screenshot({
    path: `${dir}/unsent-answer-375.png`,
    fullPage: true,
  });
  allowDialog = true;
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .dblclick();
  await page
    .getByRole("heading", {
      name: "How would you choose a threshold for this scenario?",
    })
    .waitFor();
  assert.equal(answerBodies.length, 1);
  assert.equal(answerBodies[0].answer, "An unsent answer with an example.");
  assert.equal(
    await page.getByLabel("Your answer", { exact: true }).inputValue(),
    "",
  );
  pass(
    "Text answer, cancelled departure/end/refresh preserve edits, explicit submission occurs once and advances to follow-up",
  );
  // Browser Back cancellation is tested against real browser history, not a router-only fixture.
  await page.goto(baseURL + "/interview/audit-interview?mode=text");
  // Establish a same-document previous location through the active room link.
  await page.getByRole("link", { name: "Dashboard", exact: true }).click();
  await page.goBack();
  await page.waitForTimeout(300);
  await page
    .getByLabel("Your answer", { exact: true })
    .fill("Back navigation must preserve this answer.");
  allowDialog = false;
  await page.goForward({ timeout: 2000 }).catch(() => {});
  await page.waitForTimeout(300);
  assert(page.url().includes("/interview/"));
  assert.equal(
    await page.getByLabel("Your answer", { exact: true }).inputValue(),
    "Back navigation must preserve this answer.",
  );
  allowDialog = true;
  await page.getByLabel("Your answer", { exact: true }).fill("");
  pass("Browser history departure cancellation preserves the route and draft");
  for (const track of ["technical", "hr"]) {
    const session = track === "hr" ? "audit-hr" : "audit-interview";
    await capture(
      "voice-ready-" + track,
      `/interview/${session}?mode=voice`,
      375,
    );
    await page.getByRole("button", { name: "Stop reading question" }).click();
    assert.equal(await page.evaluate(() => window.micCalls), 0);
    await page.getByRole("button", { name: "Start recording answer" }).focus();
    await page.keyboard.press("Space");
    await page.getByText("Connecting microphone", { exact: true }).waitFor();
    await captureVoiceState(`voice-connecting-${track}`);
    await page.evaluate(() => window.mockRecognizers.at(-1).begin());
    await page.getByText("Recording answer", { exact: true }).waitFor();
    await captureVoiceState(`voice-recording-${track}`);
    await page.evaluate(() => {
      const r = window.mockRecognizers.at(-1);
      r.recognized(null, {
        result: { reason: 3, text: "My answer includes a concrete example." },
      });
      r.recognizing(null, { result: { text: "pending final words" } });
    });
    assert(await page.getByLabel("Your answer", { exact: true }).isDisabled());
    const count = answerBodies.length;
    await page.getByRole("button", { name: "Stop recording answer" }).click();
    await page
      .getByText("Processing final transcript", { exact: true })
      .waitFor();
    assert(
      await page
        .getByRole("button", { name: "Submit answer", exact: true })
        .isDisabled(),
    );
    await captureVoiceState(`voice-processing-${track}`);
    await page.evaluate(() => {
      const r = window.mockRecognizers.at(-1);
      r.recognized(null, {
        result: { reason: 3, text: "That is the final sentence of my answer." },
      });
      r.finish();
    });
    await page.getByText("Transcript Review", { exact: true }).waitFor();
    const transcript = page.getByLabel("Your answer", { exact: true });
    assert(
      (await transcript.inputValue()).endsWith(
        "That is the final sentence of my answer.",
      ),
    );
    assert.equal(answerBodies.length, count);
    assert.equal(await page.evaluate(() => window.closedTracks), 1);
    await transcript.fill(
      (await transcript.inputValue()) + " Edited before submission.",
    );
    await captureVoiceState(`voice-review-${track}`);
    await page
      .getByRole("button", { name: "Submit answer", exact: true })
      .dblclick();
    await page
      .getByRole("heading", {
        name: "How would you choose a threshold for this scenario?",
      })
      .waitFor();
    assert.equal(answerBodies.length, count + 1);
    assert(answerBodies.at(-1).answer.endsWith("Edited before submission."));
    await page.getByRole("button", { name: "Text", exact: true }).click();
    assert.equal(
      await page.evaluate(() => window.mockPlayers.at(-1).paused),
      true,
    );
  }
  pass(
    "Mocked Technical and HR Voice: playback, connect, record, final drain, editable review, explicit one-time submit, text switch",
  );
  await page.goto(baseURL + "/interview/audit-interview?mode=voice");
  await page.getByRole("button", { name: "Stop reading question" }).click();
  await page.evaluate(() => (window.denyMic = true));
  await page.getByRole("button", { name: "Start recording answer" }).click();
  await page.getByText(/Microphone access was denied/).waitFor();
  await page
    .getByRole("button", { name: "Switch to Text Mode", exact: true })
    .click();
  assert(await page.getByLabel("Your answer", { exact: true }).isEnabled());
  pass("Permission denial exposes text recovery without submitting");
  resetPractice();
  practice.questions[0].attempts = [];
  practice.questions[0].hints_revealed = [];
  practice.questions[0].revealed_hints = {};
  await capture(
    "practice-first-attempt",
    "/practice/audit-practice?reportId=1&reportSessionId=audit-interview",
    375,
  );
  const help = page.locator(".learning-help summary");
  await help.focus();
  await page.keyboard.press("Enter");
  await page.getByRole("button", { name: "Get Hint 1 (Direction)" }).click();
  await page.getByRole("heading", { name: /Hint 1/ }).waitFor();
  await page.getByRole("button", { name: "Get Hint 2 (Structure)" }).click();
  await page.getByRole("heading", { name: /Hint 2/ }).waitFor();
  await page.getByRole("button", { name: "Show Reference Answer" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.waitFor();
  assert.equal(
    await page.evaluate(() => document.activeElement.textContent),
    "Cancel",
  );
  for (let i = 0; i < 5; i++) {
    await page.keyboard.press("Tab");
    assert(await dialog.evaluate((e) => e.contains(document.activeElement)));
  }
  await dialog
    .getByRole("button", { name: "Reveal Answer", exact: true })
    .click();
  await page.getByRole("heading", { name: /AI-generated example/ }).waitFor();
  assert(
    (await page.locator(".learning-main").innerText()).includes(
      "Reference-assisted",
    ),
  );
  await page
    .getByLabel("Your practice answer")
    .fill("I compare recall and precision against error costs.");
  failed.add("/practice/questions/practice-q1/attempts");
  await page
    .getByRole("button", { name: "Submit for coaching", exact: true })
    .click();
  await page.getByRole("alert").waitFor();
  assert.equal(
    await page.getByLabel("Your practice answer").inputValue(),
    "I compare recall and precision against error costs.",
  );
  await page.screenshot({
    path: `${dir}/practice-action-error-375.png`,
    fullPage: true,
  });
  failed.clear();
  await page
    .getByRole("button", { name: "Submit for coaching", exact: true })
    .dblclick();
  await page.getByRole("heading", { name: "Your next improvement" }).waitFor();
  assert.equal(practiceBodies.length, 1);
  assert.equal(
    practice.questions[0].attempts[0].assistance_level,
    "reference_assisted",
  );
  assert.equal(
    await page.evaluate(() => document.activeElement.id),
    "coaching-title",
  );
  await page
    .getByRole("button", { name: "Improve my answer", exact: true })
    .click();
  assert.equal(
    await page.evaluate(() => document.activeElement.id),
    "practice-answer",
  );
  await page
    .getByLabel("Your practice answer")
    .fill(
      "I compare recall and precision against error costs, then validate threshold choices.",
    );
  await page
    .getByRole("button", { name: "Submit improved attempt", exact: true })
    .dblclick();
  await page.getByText("What improved", { exact: true }).waitFor();
  assert.equal(practiceBodies.length, 2);
  assert.equal(
    practice.questions[0].attempts[1].assistance_level,
    "reference_assisted",
  );
  await page
    .getByText("Compare your last two attempts", { exact: true })
    .click();
  assert(
    (await page.locator(".learning-coach").innerText()).includes(
      "validate threshold choices",
    ),
  );
  await page.screenshot({
    path: `${dir}/practice-retry-comparison-375.png`,
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "Try a similar question", exact: true })
    .click();
  await page
    .getByRole("heading", {
      name: "How would you choose a decision threshold?",
    })
    .waitFor();
  assert.equal(await page.getByLabel("Your practice answer").inputValue(), "");
  await page.getByLabel("Saved question").selectOption("0");
  await page.getByRole("heading", { name: "Your next improvement" }).waitFor();
  await page
    .getByRole("link", { name: "Return to Report", exact: true })
    .click();
  assert(page.url().endsWith("/reports/audit-interview"));
  pass(
    "Progressive hints, keyboard reference confirmation, assistance persistence, failed coaching recovery, two submissions, retry focus/comparison, similar question and return to originating report",
  );
  report.interview_type = "hr";
  reportSummary.interview_type = "hr";
  rec.interview_type = "hr";
  await page.goto(baseURL + "/reports/audit-interview");
  await page
    .locator(".roadmap-item")
    .getByRole("link", { name: "Practice This Topic" })
    .click();
  await page.locator(".practice-question-text").waitFor();
  assert.equal(creates.at(-1).interview_type, "hr");
  assert.equal(creates.at(-1).source_report_id, 1);
  await page.reload();
  await page.getByRole("link", { name: "Return to Report" }).click();
  assert(page.url().endsWith("/reports/audit-interview"));
  pass(
    "HR report to practice to report retains source session and track after refresh",
  );
  await page.goto(baseURL + "/interview/audit-interview?mode=voice");
  await page.getByRole("button", { name: "Stop reading question" }).click();
  await page.getByRole("button", { name: "Start recording answer" }).click();
  await page.getByRole("button", { name: "Cancel microphone" }).click();
  await page.evaluate(() => window.mockRecognizers.at(-1).finish());
  await page.getByText("Transcript Review", { exact: true }).waitFor();
  assert.equal(await page.evaluate(() => window.closedTracks), 1);
  await page.getByRole("button", { name: "Text", exact: true }).click();
  await page.getByRole("button", { name: "Voice", exact: true }).click();
  await page.getByRole("button", { name: "Stop reading question" }).click();
  assert.equal(await page.evaluate(() => window.micCalls), 1);
  await page.getByRole("button", { name: "Start recording answer" }).click();
  await page.evaluate(() => window.mockRecognizers.at(-1).begin());
  await page.getByText("Recording answer", { exact: true }).waitFor();
  const countBeforeSwitch = answerBodies.length;
  await page.getByRole("button", { name: "Text", exact: true }).click();
  await page.evaluate(() => {
    const r = window.mockRecognizers.at(-1);
    r.recognized(null, {
      result: { reason: 3, text: "Final words after switching modes." },
    });
    r.finish();
  });
  assert.equal(
    await page.getByLabel("Your answer", { exact: true }).inputValue(),
    "Final words after switching modes.",
  );
  assert.equal(await page.evaluate(() => window.closedTracks), 2);
  assert.equal(answerBodies.length, countBeforeSwitch);
  pass(
    "Rapid microphone cancellation and Voice/Text switching drain final words, release tracks and never submit",
  );
  await page.getByLabel("Your answer", { exact: true }).fill("");
  failed.add("/interview/audit-interview");
  await page.goto(baseURL + "/interview/audit-interview?mode=text");
  await page.getByRole("button", { name: "Retry", exact: true }).waitFor();
  failed.clear();
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  await page.getByLabel("Your answer", { exact: true }).waitFor();
  await page
    .getByRole("button", { name: "End interview", exact: true })
    .click();
  await page
    .getByRole("heading", {
      name: "Machine Learning Engineer Interview Complete",
    })
    .waitFor();
  await captureVoiceState("interview-complete");
  failed.add("/practice/sessions/audit-practice");
  await page.goto(baseURL + "/practice/audit-practice");
  await page.getByRole("button", { name: "Retry", exact: true }).waitFor();
  failed.clear();
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  await page.locator(".practice-question-text").waitFor();
  resetPractice();
  practice.questions[0].attempts[0].feedback.evaluation_status = "unavailable";
  await page.goto(baseURL + "/practice/audit-practice");
  await page.getByText(/Coaching is unavailable for this attempt/).waitFor();
  await captureVoiceState("practice-coaching-unavailable");
  pass(
    "Interview/practice load retries recover, completion controls and unavailable coaching fit at every width",
  );
  assert(dialogs.some((d) => d.type === "beforeunload"));
  assert(dialogs.some((d) => d.message.includes("Drafts are not saved")));
  await writeFile(
    `${dir}/results.json`,
    JSON.stringify(
      { passed, observations, answerBodies, practiceBodies, dialogs, errors },
      null,
      2,
    ),
  );
  console.log(JSON.stringify({ groups: passed.length, status: "PASS" }));
} finally {
  await browser.close();
  devServer?.kill();
}
