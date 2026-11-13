import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  ArrowRightIcon,
  BarChartIcon,
  BookOpenIcon,
  CheckCircleIcon,
  CodeIcon,
  CompassIcon,
  FileTextIcon,
  GraduationCapIcon,
  LightbulbIcon,
  MenuIcon,
  MessageSquareIcon,
  RotateCcwIcon,
  ShieldCheckIcon,
  SparklesIcon,
  TargetIcon,
  UsersIcon,
  XIcon,
  ZapIcon,
} from "../components/Icons";
import "./Landing.css";

export default function Landing() {
  const { user } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"resume" | "interview" | "practice" | "report">("resume");

  return (
    <div className="landing-root">
      {/* ─── A. Navigation Bar ─── */}
      <header className="landing-nav-header">
        <div className="landing-container landing-nav-inner">
          <Link to="/" className="landing-brand">
            <span className="landing-brand-mark">
              <GraduationCapIcon size={20} />
            </span>
            <div className="landing-brand-text">
              <span className="landing-brand-title">PrepMate</span>
              <span className="landing-brand-badge">AI Coach</span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="landing-desktop-nav" aria-label="Landing navigation">
            <a href="#how-it-works" className="landing-nav-link">How It Works</a>
            <a href="#features" className="landing-nav-link">Features</a>
            <a href="#showcase" className="landing-nav-link">Interactive Tour</a>
            <a href="#why-prepmate" className="landing-nav-link">Why PrepMate</a>
          </nav>

          <div className="landing-nav-actions">
            {user ? (
              <Link to="/dashboard" className="btn btn-primary btn-sm">
                <span>Go to Dashboard</span>
                <ArrowRightIcon size={14} />
              </Link>
            ) : (
              <>
                <Link to="/login" className="btn btn-ghost btn-sm">
                  Sign In
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm">
                  <span>Get Started</span>
                  <ArrowRightIcon size={14} />
                </Link>
              </>
            )}

            <button
              type="button"
              className="landing-mobile-toggle"
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              aria-label={mobileNavOpen ? "Close navigation" : "Open navigation"}
            >
              {mobileNavOpen ? <XIcon size={20} /> : <MenuIcon size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        {mobileNavOpen && (
          <div className="landing-mobile-menu">
            <a
              href="#how-it-works"
              className="landing-mobile-link"
              onClick={() => setMobileNavOpen(false)}
            >
              How It Works
            </a>
            <a
              href="#features"
              className="landing-mobile-link"
              onClick={() => setMobileNavOpen(false)}
            >
              Features
            </a>
            <a
              href="#showcase"
              className="landing-mobile-link"
              onClick={() => setMobileNavOpen(false)}
            >
              Interactive Tour
            </a>
            <a
              href="#why-prepmate"
              className="landing-mobile-link"
              onClick={() => setMobileNavOpen(false)}
            >
              Why PrepMate
            </a>
            <div className="landing-mobile-cta">
              {user ? (
                <Link
                  to="/dashboard"
                  className="btn btn-primary"
                  onClick={() => setMobileNavOpen(false)}
                >
                  Go to Dashboard
                </Link>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="btn btn-secondary"
                    onClick={() => setMobileNavOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="btn btn-primary"
                    onClick={() => setMobileNavOpen(false)}
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </header>

      <main>
        {/* ─── B. Hero Section ─── */}
        <section className="landing-hero-section">
          <div className="landing-container">
            <div className="landing-hero-inner">
              <div className="landing-hero-copy">
                <div className="landing-eyebrow-pill">
                  <span className="pulse-dot" />
                  <span>Resume-grounded interview practice</span>
                </div>
                <h1 className="landing-hero-title">
                  Prepare Smarter.
                  <br />
                  <span className="accent-text">Interview Better.</span>
                </h1>
                <p className="landing-hero-sub">
                  From resume analysis to personalized mock interviews and guided practice,
                  PrepMate helps you understand your strengths, improve your weaknesses,
                  and prepare with confidence.
                </p>

                <div className="landing-hero-cta-group">
                  <Link to="/register" className="btn btn-primary landing-cta-primary">
                    <span>Start Preparing Free</span>
                    <ArrowRightIcon size={16} />
                  </Link>
                  <a href="#showcase" className="btn btn-secondary landing-cta-secondary">
                    <span>Explore Features</span>
                  </a>
                </div>

                <div className="landing-hero-trust-strip">
                  <div className="trust-pill">
                    <CheckCircleIcon size={14} />
                    <span>Evidence-aware resume matching</span>
                  </div>
                  <div className="trust-pill">
                    <CheckCircleIcon size={14} />
                    <span>Adaptive interview difficulty</span>
                  </div>
                  <div className="trust-pill">
                    <CheckCircleIcon size={14} />
                    <span>Structured AI answer feedback</span>
                  </div>
                </div>
              </div>

              {/* Realistic Hero Product Preview — Clean, layered, focused on AI Interview & Coaching */}
              <div className="landing-hero-preview-col">
                <div className="landing-hero-browser-card">
                  <div className="browser-header">
                    <div className="browser-dots">
                      <span className="dot dot-red" />
                      <span className="dot dot-yellow" />
                      <span className="dot dot-green" />
                    </div>
                    <div className="browser-address-bar">
                      <span>prepmate.ai/interview/live</span>
                    </div>
                    <span className="badge badge-accent badge-pulse">Live Session</span>
                  </div>

                  <div className="hero-product-content">
                    {/* Live Question Block */}
                    <div className="hero-question-panel">
                      <div className="hero-q-meta">
                        <span className="badge badge-neutral">Question 3 of 8</span>
                        <span className="hero-q-difficulty">Technical · Adaptive Medium</span>
                      </div>
                      <h3 className="hero-q-title">
                        &ldquo;How would you handle a sudden 10x traffic spike on a payment webhook service to prevent database exhaustion?&rdquo;
                      </h3>
                    </div>

                    {/* Candidate Answer Preview */}
                    <div className="hero-answer-box">
                      <div className="hero-answer-label">Candidate Answer</div>
                      <p className="hero-answer-text">
                        &ldquo;I would place a distributed message queue in front of the database to decouple write ingestion from persistence, and apply rate limiting with exponential backoff...&rdquo;
                      </p>
                    </div>

                    {/* AI Coach Live Feedback Card */}
                    <div className="hero-coach-feedback">
                      <div className="hero-coach-header">
                        <SparklesIcon size={15} />
                        <strong>AI Answer Coach</strong>
                        <span className="badge badge-success">Strong Answer · 88%</span>
                      </div>
                      <div className="hero-coach-points">
                        <div className="hero-coach-point pos">
                          <CheckCircleIcon size={13} />
                          <span><strong>Key Strength:</strong> Effective decoupling pattern with queue-based buffer.</span>
                        </div>
                        <div className="hero-coach-point ref">
                          <LightbulbIcon size={13} />
                          <span><strong>Opportunity:</strong> Mention idempotency keys to safely process duplicate webhook retries.</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ─── C. How PrepMate Works ─── */}
        <section id="how-it-works" className="landing-section landing-process-section">
          <div className="landing-container">
            <div className="landing-section-head">
              <span className="landing-section-eyebrow">HOW IT WORKS</span>
              <h2 className="landing-section-title">A clear path from resume to offer</h2>
              <p className="landing-section-sub">
                Four straightforward steps designed to build genuine interview confidence and technical clarity.
              </p>
            </div>

            <div className="landing-process-grid">
              <div className="process-step-card">
                <div className="process-step-num">01</div>
                <div className="process-icon-wrap">
                  <FileTextIcon size={24} />
                </div>
                <h3 className="process-step-title">Upload Your Resume</h3>
                <p className="process-step-desc">
                  Upload your PDF resume and target role. PrepMate extracts validated technical experience, project context, and competencies.
                </p>
                <div className="process-tag-list">
                  <span>PDF Parsing</span>
                  <span>Role Calibration</span>
                </div>
              </div>

              <div className="process-step-card">
                <div className="process-step-num">02</div>
                <div className="process-icon-wrap">
                  <TargetIcon size={24} />
                </div>
                <h3 className="process-step-title">Understand Your Strengths</h3>
                <p className="process-step-desc">
                  Discover matched proficiencies and role-specific skill gaps with rubric-based alignment scores and evidence tracing.
                </p>
                <div className="process-tag-list">
                  <span>Match Score</span>
                  <span>Observed Gaps</span>
                </div>
              </div>

              <div className="process-step-card">
                <div className="process-step-num">03</div>
                <div className="process-icon-wrap">
                  <MessageSquareIcon size={24} />
                </div>
                <h3 className="process-step-title">Practice Real Interviews</h3>
                <p className="process-step-desc">
                  Take adaptive technical or HR interviews that dynamically calibrate difficulty in real time based on your demonstrated answers.
                </p>
                <div className="process-tag-list">
                  <span>Dynamic Pacing</span>
                  <span>HR & Technical</span>
                </div>
              </div>

              <div className="process-step-card">
                <div className="process-step-num">04</div>
                <div className="process-icon-wrap">
                  <SparklesIcon size={24} />
                </div>
                <h3 className="process-step-title">Learn and Improve</h3>
                <p className="process-step-desc">
                  Receive structured breakdown reports, practice weak areas with progressive hints, and retry answers with instant AI feedback.
                </p>
                <div className="process-tag-list">
                  <span>Progressive Hints</span>
                  <span>AI Coaching</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ─── D. Features Section (Bento Grid) ─── */}
        <section id="features" className="landing-section landing-features-section">
          <div className="landing-container">
            <div className="landing-section-head">
              <span className="landing-section-eyebrow">FEATURES</span>
              <h2 className="landing-section-title">Built for serious interview preparation</h2>
              <p className="landing-section-sub">
                Targeted resume analysis, adaptive interview simulation, and actionable answer coaching.
              </p>
            </div>

            <div className="bento-grid">
              {/* Feature 1: Large Bento Card */}
              <div className="bento-card bento-wide">
                <div className="bento-copy">
                  <span className="bento-badge">Resume Intelligence</span>
                  <h3 className="bento-title">Smart Resume Analysis & Gap Identification</h3>
                  <p className="bento-desc">
                    Evidence-aware parsing evaluates your concrete experience against your target job description. We highlight exact matched skills, missing prerequisites, and tailored practice priorities.
                  </p>
                  <ul className="bento-bullets">
                    <li><CheckCircleIcon size={14} /> Deterministic skill taxonomy mapping</li>
                    <li><CheckCircleIcon size={14} /> No duplicate uploads — smart hash deduplication</li>
                    <li><CheckCircleIcon size={14} /> Contextual strengths vs. target role requirements</li>
                  </ul>
                </div>
                <div className="bento-visual bento-visual-resume">
                  <div className="sim-skill-tags">
                    <span className="skill-tag match">PostgreSQL 94%</span>
                    <span className="skill-tag match">FastAPI 90%</span>
                    <span className="skill-tag match">React & TS 88%</span>
                    <span className="skill-tag gap">Distributed Systems — Gap</span>
                    <span className="skill-tag match">Docker 82%</span>
                  </div>
                </div>
              </div>

              {/* Feature 2: Standard Bento Card */}
              <div className="bento-card">
                <div className="bento-icon-box">
                  <CompassIcon size={22} />
                </div>
                <h3 className="bento-title">Adaptive Difficulty Engine</h3>
                <p className="bento-desc">
                  Questions adjust dynamically based on your answer quality. Excel on foundational concepts, and PrepMate introduces realistic production constraints and trade-offs.
                </p>
              </div>

              {/* Feature 3: Standard Bento Card */}
              <div className="bento-card">
                <div className="bento-icon-box">
                  <UsersIcon size={22} />
                </div>
                <h3 className="bento-title">Dual Interview Modes: Tech & HR</h3>
                <p className="bento-desc">
                  Switch seamlessly between deep technical architecture rounds and behavioral STAR-method interviews covering conflict resolution, decision trade-offs, and leadership.
                </p>
              </div>

              {/* Feature 4: Standard Bento Card */}
              <div className="bento-card">
                <div className="bento-icon-box">
                  <LightbulbIcon size={22} />
                </div>
                <h3 className="bento-title">Progressive Hints & References</h3>
                <p className="bento-desc">
                  Stuck on a tricky scenario? Unlock Level 1 gentle architectural clues or Level 2 structured frameworks without spoiling the final answer.
                </p>
              </div>

              {/* Feature 5: Wide Bento Card */}
              <div className="bento-card bento-wide">
                <div className="bento-copy">
                  <span className="bento-badge">Answer Coaching</span>
                  <h3 className="bento-title">Personalized Practice Studio & Instant Feedback</h3>
                  <p className="bento-desc">
                    Unlike standard mock exams that grade you and leave, PrepMate's Practice Studio allows iterative answer improvement with side-by-side coaching on structure, missed concepts, and communication.
                  </p>
                  <ul className="bento-bullets">
                    <li><CheckCircleIcon size={14} /> &ldquo;Improve My Answer&rdquo; comparative retry diffs</li>
                    <li><CheckCircleIcon size={14} /> Rubric dimension breakdown across 5 core competencies</li>
                    <li><CheckCircleIcon size={14} /> Similar concept transfers to build true intuition</li>
                  </ul>
                </div>
                <div className="bento-visual bento-visual-coach">
                  <div className="sim-coach-pill">
                    <strong>Structure:</strong> Strong opening & trade-off clarity
                  </div>
                  <div className="sim-coach-pill warn">
                    <strong>Missing Concept:</strong> Concurrency controls under lock contention
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ─── E. Interactive Product Showcase ─── */}
        <section id="showcase" className="landing-section landing-showcase-section">
          <div className="landing-container">
            <div className="landing-section-head">
              <span className="landing-section-eyebrow">PRODUCT TOUR</span>
              <h2 className="landing-section-title">See PrepMate in Action</h2>
              <p className="landing-section-sub">
                Explore authentic views of the platform designed to elevate your interview readiness.
              </p>
            </div>

            {/* Tab Controls */}
            <div className="showcase-tabs" role="tablist">
              <button
                type="button"
                className={`showcase-tab ${activeTab === "resume" ? "active" : ""}`}
                onClick={() => setActiveTab("resume")}
              >
                <FileTextIcon size={16} />
                <span>Resume Analysis</span>
              </button>
              <button
                type="button"
                className={`showcase-tab ${activeTab === "interview" ? "active" : ""}`}
                onClick={() => setActiveTab("interview")}
              >
                <MessageSquareIcon size={16} />
                <span>Interview Room</span>
              </button>
              <button
                type="button"
                className={`showcase-tab ${activeTab === "practice" ? "active" : ""}`}
                onClick={() => setActiveTab("practice")}
              >
                <BookOpenIcon size={16} />
                <span>Practice Studio</span>
              </button>
              <button
                type="button"
                className={`showcase-tab ${activeTab === "report" ? "active" : ""}`}
                onClick={() => setActiveTab("report")}
              >
                <BarChartIcon size={16} />
                <span>Performance Report</span>
              </button>
            </div>

            {/* Tab Display Window */}
            <div className="showcase-display-window">
              {activeTab === "resume" && (
                <div className="showcase-view-panel">
                  <div className="showcase-panel-header">
                    <div>
                      <span className="badge badge-accent">Resume Analysis</span>
                      <h3>Machine Learning Engineer · 78% Match</h3>
                    </div>
                    <span className="showcase-tag">Grounded in uploaded PDF</span>
                  </div>
                  <div className="showcase-grid-2">
                    <div className="showcase-card">
                      <h4 className="card-subhead">Validated Technical Strengths</h4>
                      <div className="skill-chip-group">
                        <span className="chip chip-success">Python & PyTorch</span>
                        <span className="chip chip-success">Transformers / HuggingFace</span>
                        <span className="chip chip-success">Vector DBs & Embeddings</span>
                        <span className="chip chip-success">PostgreSQL & SQL</span>
                      </div>
                    </div>
                    <div className="showcase-card">
                      <h4 className="card-subhead">Identified Improvement Priorities</h4>
                      <div className="gap-alert-item">
                        <strong>Model Quantization & TensorRT</strong>
                        <p>Target role requires low-latency inference on edge clusters.</p>
                      </div>
                      <div className="gap-alert-item">
                        <strong>MLOps Deployment Pipelines</strong>
                        <p>Kubeflow or Triton serving experience recommended.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "interview" && (
                <div className="showcase-view-panel">
                  <div className="showcase-panel-header">
                    <div>
                      <span className="badge badge-accent">Live Mock Session</span>
                      <h3>Question 2 of 8 — Adaptive Technical</h3>
                    </div>
                    <span className="badge badge-warning">Medium Difficulty</span>
                  </div>
                  <div className="showcase-q-box">
                    <p className="q-text">
                      &ldquo;You are architecting a real-time notification service handling 100k writes/sec. How would you prevent message loss while keeping tail latency under 50ms?&rdquo;
                    </p>
                    <div className="sim-answer-preview">
                      <div className="sim-editor-line">
                        <em>Candidate Answer:</em> &ldquo;I would introduce an event bus like Kafka or RabbitMQ with partitioned queues...&rdquo;
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "practice" && (
                <div className="showcase-view-panel">
                  <div className="showcase-panel-header">
                    <div>
                      <span className="badge badge-accent">Guided Practice Studio</span>
                      <h3>Target Topic: Distributed Lock Managers</h3>
                    </div>
                    <span className="badge badge-success">Self-Paced</span>
                  </div>
                  <div className="showcase-grid-2">
                    <div className="showcase-card">
                      <h4 className="card-subhead">Progressive Hint Clues</h4>
                      <div className="hint-pill">
                        <strong>Hint 1 (Gentle Direction):</strong>
                        <p>Consider what happens if the lock-holding client crashes before releasing.</p>
                      </div>
                      <div className="hint-pill">
                        <strong>Hint 2 (Framework Clue):</strong>
                        <p>Evaluate Redlock algorithm trade-offs vs. single Redis master with lease TTLs.</p>
                      </div>
                    </div>
                    <div className="showcase-card">
                      <h4 className="card-subhead">AI Coach Feedback</h4>
                      <div className="coach-pill-item good">
                        <strong>Strength:</strong> Thorough breakdown of TTL lease renewal.
                      </div>
                      <div className="coach-pill-item improve">
                        <strong>Refinement:</strong> Address split-brain risks under network partitions.
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "report" && (
                <div className="showcase-view-panel">
                  <div className="showcase-panel-header">
                    <div>
                      <span className="badge badge-accent">Comprehensive Evaluation Report</span>
                      <h3>Overall Score: 85 / 100 · Senior SDE</h3>
                    </div>
                    <span className="badge badge-success">Passed Benchmark</span>
                  </div>
                  <div className="report-rubric-grid">
                    <div className="rubric-stat">
                      <span className="rubric-label">Technical Correctness</span>
                      <strong className="rubric-num">90%</strong>
                      <div className="rubric-bar"><div className="rubric-fill" style={{ width: "90%" }} /></div>
                    </div>
                    <div className="rubric-stat">
                      <span className="rubric-label">System Architecture</span>
                      <strong className="rubric-num">85%</strong>
                      <div className="rubric-bar"><div className="rubric-fill" style={{ width: "85%" }} /></div>
                    </div>
                    <div className="rubric-stat">
                      <span className="rubric-label">Trade-Off Analysis</span>
                      <strong className="rubric-num">80%</strong>
                      <div className="rubric-bar"><div className="rubric-fill" style={{ width: "80%" }} /></div>
                    </div>
                    <div className="rubric-stat">
                      <span className="rubric-label">Communication & Clarity</span>
                      <strong className="rubric-num">85%</strong>
                      <div className="rubric-bar"><div className="rubric-fill" style={{ width: "85%" }} /></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* ─── F. Why PrepMate? ─── */}
        <section id="why-prepmate" className="landing-section landing-why-section">
          <div className="landing-container">
            <div className="landing-section-head">
              <span className="landing-section-eyebrow">WHY PREPMATE</span>
              <h2 className="landing-section-title">Designed for interviews, not conversation</h2>
              <p className="landing-section-sub">
                Generic chatbots ask random questions and give surface-level feedback. PrepMate evaluates your real skills against specific job requirements.
              </p>
            </div>

            <div className="comparison-table-wrap">
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Capability</th>
                    <th>Generic Interview Chatbot</th>
                    <th className="highlight-col">PrepMate Platform</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Personalization</strong></td>
                    <td>Generic prompt-based questions without resume context</td>
                    <td className="highlight-col"><strong>Grounds questions in your specific resume & target role</strong></td>
                  </tr>
                  <tr>
                    <td><strong>Difficulty Progression</strong></td>
                    <td>Static difficulty or random jumping between easy/hard</td>
                    <td className="highlight-col"><strong>Calibrated dynamic difficulty based on live answer evaluations</strong></td>
                  </tr>
                  <tr>
                    <td><strong>Interview Breadth</strong></td>
                    <td>Only surface-level coding trivia or basic HR prompts</td>
                    <td className="highlight-col"><strong>Dedicated Technical & HR behavioral engines with tailored rubrics</strong></td>
                  </tr>
                  <tr>
                    <td><strong>Learning Support</strong></td>
                    <td>Either gives the full answer away or offers vague feedback</td>
                    <td className="highlight-col"><strong>2-stage progressive hints, reference blueprints, and answer retries</strong></td>
                  </tr>
                  <tr>
                    <td><strong>Evaluation Quality</strong></td>
                    <td>Single holistic score with sycophantic approval</td>
                    <td className="highlight-col"><strong>Multi-dimensional rubric scoring with explicit gap identification</strong></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* ─── G. Final Call to Action ─── */}
        <section className="landing-cta-banner-section">
          <div className="landing-container">
            <div className="landing-cta-banner">
              <div className="cta-banner-copy">
                <span className="landing-section-eyebrow" style={{ color: "var(--accent)" }}>START PREPARING TODAY</span>
                <h2 className="cta-banner-title">Your next interview starts with better preparation.</h2>
                <p className="cta-banner-desc">
                  Understand where you stand, practice what matters, and build unshakeable confidence for your dream role.
                </p>
              </div>
              <div className="cta-banner-action">
                <Link to="/register" className="btn btn-primary landing-cta-large">
                  <span>Get Started</span>
                  <ArrowRightIcon size={16} />
                </Link>
                <span className="cta-banner-hint">Free setup · Instant access</span>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* ─── H. Footer ─── */}
      <footer className="landing-footer">
        <div className="landing-container landing-footer-inner">
          <div className="footer-col-brand">
            <Link to="/" className="landing-brand">
              <span className="landing-brand-mark">
                <GraduationCapIcon size={18} />
              </span>
              <span className="landing-brand-title">PrepMate</span>
            </Link>
            <p className="footer-brand-desc">
              AI-powered resume analysis, adaptive technical and behavioral interviews, and personalized practice coaching.
            </p>
          </div>

          <div className="footer-links-grid">
            <div className="footer-col">
              <h4>Navigation</h4>
              <ul>
                <li><a href="#how-it-works">How It Works</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#showcase">Product Tour</a></li>
                <li><a href="#why-prepmate">Why PrepMate</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h4>Get Started</h4>
              <ul>
                <li><Link to="/register">Create Account</Link></li>
                <li><Link to="/login">Sign In</Link></li>
                <li><Link to="/dashboard">Dashboard</Link></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="landing-container footer-bottom-bar">
          <p>© {new Date().getFullYear()} PrepMate. Built for focused career readiness.</p>
        </div>
      </footer>
    </div>
  );
}
