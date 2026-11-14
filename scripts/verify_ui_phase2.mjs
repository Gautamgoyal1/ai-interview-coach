import assert from "node:assert/strict";
import { chromium } from "../storage/voice-acceptance/node_modules/playwright/index.mjs";
import { mkdir, writeFile } from "node:fs/promises";
const dir = "storage/ui-phase2";
await mkdir(dir, { recursive: true });
const starts = [];
const calls = {};
const checks = [];
function pass(check) {
  checks.push(check);
  console.log(JSON.stringify({ check, status: "PASS" }));
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
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.port !== "8000") return route.continue();
    const p = url.pathname;
    calls[p] = (calls[p] || 0) + 1;
    if (p === "/interview/start") {
      const body = route.request().postDataJSON();
      starts.push(body);
      return route.fulfill({
        status: 201,
        json: {
          ...interview,
          interview_type: body.interview_type,
          experience_level: body.experience_level,
          starting_difficulty: body.starting_difficulty,
          progression_mode: body.progression_mode,
          max_questions: body.max_questions,
        },
      });
    }
    if (scenario === "partial" && p === "/resume/analyses")
      return route.fulfill({
        status: 503,
        json: { detail: "Resume history temporarily unavailable" },
      });
    if (scenario === "slow-recs" && p === "/practice/recommendations")
      await new Promise((r) => setTimeout(r, 2500));
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
      return route.fulfill({ json: practice });
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
  async function capture(name, route, width = 1440, mode = "populated") {
    scenario = mode;
    errors.length = 0;
    await page.setViewportSize({ width, height: 1000 });
    await page.goto("http://localhost:5173" + route);
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
      .locator("main a,main button,main input,main select,main textarea")
      .evaluateAll((es) =>
        es
          .filter(
            (e) =>
              e.getClientRects().length &&
              getComputedStyle(e).visibility === "visible",
          )
          .map((e) => {
            const b = e.getBoundingClientRect();
            return { tag: e.tagName, left: b.left, right: b.right };
          })
          .filter((b) => b.left < -1 || b.right > innerWidth + 1),
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

  for (const width of [320, 375, 768, 1440]) {
    await capture("dashboard", "/dashboard", width);
    const primary = page.locator(".prep-dashboard .btn-primary");
    assert.equal(await primary.count(), 1);
    assert.equal(await primary.innerText(), "Practice This Topic");
    assert((await primary.getAttribute("href")).includes("reportId=1"));
    await capture("setup", "/interview?analysisId=2", width);
    assert.equal(
      await page.getByLabel("Resume profile", { exact: true }).inputValue(),
      "2",
    );
    assert(
      await page
        .getByRole("radio", { name: "Text Type and edit your answers." })
        .isChecked(),
    );
    assert.equal(calls["/speech/synthesize"] || 0, 0);
    assert.equal(starts.length, 0);
    await page.getByRole("radio", { name: /Technical Skills/ }).focus();
    await page.keyboard.press("ArrowRight");
    assert(await page.getByRole("radio", { name: /HR \/ Behavioral/ }).isChecked());
    await page.getByRole("radio", { name: /Text Type/ }).focus();
    await page.keyboard.press("ArrowRight");
    assert(await page.getByRole("radio", { name: /Voice Speak/ }).isChecked());
    const summary = page.locator(".setup-advanced>summary");
    await summary.focus();
    await page.keyboard.press("Enter");
    assert(
      await page.getByRole("radio", { name: /Mock Assessment/ }).isVisible(),
    );
    await page.getByRole("radio", { name: /Mock Assessment/ }).check();
    await page.getByRole("radio", { name: /HR \/ Behavioral/ }).check();
    await page.getByRole("radio", { name: /Voice Speak/ }).check();
    await page
      .getByLabel("Experience level", { exact: true })
      .selectOption("internship");
    assert.equal(
      await page
        .getByLabel("Starting difficulty", { exact: true })
        .inputValue(),
      "easy",
    );
    await page
      .getByLabel("Starting difficulty", { exact: true })
      .selectOption("hard");
    await page.getByRole("radio", { name: "10 questions More depth" }).check();
    await page.screenshot({
      path: `${dir}/setup-advanced-${width}.png`,
      fullPage: true,
    });
    pass(
      `returning-user layout, native keyboard controls and all options at ${width}px`,
    );
  }
  await capture("dashboard-empty", "/dashboard", 1440, "empty");
  assert.equal(
    await page.locator(".prep-dashboard .btn-primary").innerText(),
    "Analyze Resume",
  );
  await capture("setup-empty", "/interview", 375, "empty");
  assert(
    await page
      .getByRole("heading", { name: "Start with your resume" })
      .isVisible(),
  );
  assert.equal(
    await page.getByRole("button", { name: /Start .* Interview/ }).count(),
    0,
  );
  await capture("dashboard-loading", "/dashboard", 1440, "loading");
  assert(await page.getByRole("status").first().isVisible());
  await capture("setup-loading", "/interview", 375, "loading");
  assert(
    await page
      .getByRole("button", { name: "Start Technical Interview", exact: true })
      .isDisabled(),
  );
  await capture("dashboard-partial", "/dashboard", 768, "partial");
  assert((await page.locator("body").innerText()).includes("68 / 100"));
  assert(
    (await page.locator("body").innerText()).includes(
      "Resume history unavailable.",
    ),
  );
  assert.equal(
    await page.locator(".prep-dashboard .btn-primary").innerText(),
    "Practice This Topic",
  );
  await capture("dashboard-error", "/dashboard", 375, "error");
  assert(
    await page
      .getByRole("heading", {
        name: "Your workspace is temporarily incomplete",
      })
      .isVisible(),
  );
  await capture("setup-error", "/interview", 375, "error");
  assert(
    await page
      .getByRole("button", { name: "Start Technical Interview", exact: true })
      .isDisabled(),
  );
  scenario = "populated";
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  await page.getByLabel("Resume profile", { exact: true }).selectOption("2");
  assert(
    await page
      .getByRole("button", { name: "Start Technical Interview", exact: true })
      .isEnabled(),
  );
  pass("new-user, loading, partial failure, all-error and setup recovery");
  // Healthy panels render while recommendations are still loading.
  scenario = "slow-recs";
  await page.goto("http://localhost:5173/dashboard");
  await page
    .locator(".command-measure strong")
    .filter({ hasText: "72" })
    .first()
    .waitFor();
  assert(
    await page
      .getByText("Loading practice recommendations...", { exact: true })
      .isVisible(),
  );
  await page
    .getByRole("link", { name: "Practice This Topic", exact: true })
    .waitFor();
  pass("independent panel loading");
  // Resume-only state should configure a round rather than repeatedly review reports.
  await page.route("**/reports?*", (route) => route.fulfill({ json: [] }));
  await page.route("**/practice/recommendations?*", (route) =>
    route.fulfill({ json: [] }),
  );
  await capture("dashboard-resume-ready", "/dashboard", 1440);
  assert.equal(
    await page.locator(".prep-dashboard .btn-primary").innerText(),
    "Set Up Interview",
  );
  await page.unroute("**/reports?*");
  await page.unroute("**/practice/recommendations?*");
  await capture("setup-launch", "/interview?analysisId=2");
  await page.getByRole("radio", { name: /HR \/ Behavioral/ }).check();
  await page.getByRole("radio", { name: /Voice Speak/ }).check();
  await page
    .getByLabel("Starting difficulty", { exact: true })
    .selectOption("hard");
  await page.getByRole("radio", { name: "5 questions Short round" }).check();
  await page.locator(".setup-advanced>summary").click();
  await page.getByRole("radio", { name: /Mock Assessment/ }).check();
  await page
    .getByRole("button", { name: "Start HR Interview", exact: true })
    .dblclick();
  await page.locator(".iv-question-text").waitFor();
  assert.equal(starts.length, 1);
  assert.deepEqual(starts[0], {
    analysis_id: 2,
    interview_type: "hr",
    experience_level: "fresher",
    starting_difficulty: "hard",
    progression_mode: "mock",
    max_questions: 5,
    max_follow_ups: 1,
  });
  pass("explicit HR Voice Mock launch preserves API contract and submits once");
  await page.goto("http://localhost:5173/interview");
  await page.getByRole("radio", { name: /Text Type/ }).check();
  await page
    .getByRole("button", { name: "Start Technical Interview", exact: true })
    .click();
  await page.locator(".iv-question-text").waitFor();
  assert.equal(starts.length, 2);
  assert.equal(starts[1].interview_type, "technical");
  assert.equal(starts[1].progression_mode, "adaptive");
  assert(page.url().includes("mode=text"));
  pass("explicit Technical Text Adaptive launch");
  for (const width of [320, 375, 768, 1440]) {
    for (const mode of ["empty", "loading", "error"]) {
      await capture(`dashboard-${mode}`, "/dashboard", width, mode);
      await capture(`setup-${mode}`, "/interview", width, mode);
    }
    await capture("dashboard-partial", "/dashboard", width, "partial");
  }
  pass("responsive empty, loading, partial-failure and error-state matrix");
  await writeFile(
    `${dir}/results.json`,
    JSON.stringify({ checks, starts, calls, observations }, null, 2),
  );
} finally {
  await browser.close();
}
