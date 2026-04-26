"""Premium landing page for the SecureReview OpenEnv Space."""

LANDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SecureReview — Security review for the age of AI</title>
<meta name="description" content="An OpenEnv environment for AI-powered security code review across dependency supply chains, infrastructure-as-code, and database migrations.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0a;
    --bg-elevated: #0f0f0f;
    --bg-hover: #141414;
    --border: #1a1a1a;
    --border-bright: #262626;
    --text: #fafafa;
    --text-dim: #a1a1a1;
    --text-subtle: #525252;
    --text-muted: #3f3f3f;
    --accent: #ff6b35;
    --accent-glow: rgba(255, 107, 53, 0.15);
    --cyan: #22d3ee;
    --mono: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  html {
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
    font-size: 15px;
    line-height: 1.6;
    letter-spacing: -0.01em;
    min-height: 100vh;
    overflow-x: hidden;
    font-weight: 300;
  }

  /* Subtle grain overlay */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    z-index: 100;
  }

  /* Ambient gradient behind hero */
  .ambient {
    position: fixed;
    top: -20%;
    left: 50%;
    transform: translateX(-50%);
    width: 1200px;
    height: 700px;
    background: radial-gradient(ellipse at center, var(--accent-glow) 0%, transparent 60%);
    pointer-events: none;
    z-index: -1;
    filter: blur(80px);
  }

  .container {
    max-width: 1040px;
    margin: 0 auto;
    padding: 56px 40px 120px;
  }

  /* NAV */
  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 80px;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text);
  }

  .brand-mark {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 12px var(--accent);
    animation: pulse 2.8s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
  }

  .nav-version {
    color: var(--text-subtle);
    font-weight: 400;
  }

  .nav-links {
    display: flex;
    gap: 32px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 400;
  }

  .nav-links a {
    color: var(--text-dim);
    text-decoration: none;
    transition: color 200ms ease;
    letter-spacing: 0.02em;
  }

  .nav-links a:hover { color: var(--text); }

  /* HERO */
  .hero {
    padding-bottom: 80px;
    max-width: 820px;
  }

  .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 40px;
    padding: 6px 14px;
    border: 1px solid var(--border-bright);
    border-radius: 100px;
    background: rgba(255, 107, 53, 0.04);
  }

  .eyebrow::before {
    content: '';
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
  }

  .hero h1 {
    font-family: var(--sans);
    font-size: clamp(44px, 8vw, 96px);
    font-weight: 200;
    letter-spacing: -0.045em;
    line-height: 0.95;
    margin-bottom: 40px;
    color: var(--text);
  }

  .hero h1 em {
    font-style: italic;
    font-weight: 300;
    color: var(--text-subtle);
  }

  .hero p {
    font-size: 20px;
    line-height: 1.55;
    color: var(--text-dim);
    font-weight: 300;
    max-width: 640px;
    letter-spacing: -0.015em;
  }

  .hero-cta {
    margin-top: 48px;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 13px 22px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    text-decoration: none;
    border: 1px solid var(--border-bright);
    color: var(--text);
    background: var(--bg-elevated);
    transition: all 200ms ease;
    border-radius: 6px;
  }

  .btn:hover {
    background: var(--bg-hover);
    border-color: var(--text-subtle);
    transform: translateY(-1px);
  }

  .btn.primary {
    background: var(--text);
    color: var(--bg);
    border-color: var(--text);
  }

  .btn.primary:hover {
    background: #e0e0e0;
    border-color: #e0e0e0;
  }

  .btn-arrow {
    display: inline-block;
    transition: transform 200ms ease;
  }

  .btn:hover .btn-arrow { transform: translateX(3px); }

  /* THESIS */
  .thesis {
    margin-bottom: 80px;
    padding: 60px 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 60px;
    align-items: start;
  }

  .thesis-label {
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding-top: 10px;
  }

  .thesis-body {
    font-size: 22px;
    line-height: 1.5;
    font-weight: 200;
    color: var(--text);
    letter-spacing: -0.02em;
    max-width: 680px;
  }

  .thesis-body strong {
    font-weight: 400;
    color: var(--text);
  }

  .thesis-body .muted {
    color: var(--text-subtle);
  }

  /* STATS */
  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    margin-bottom: 80px;
    border-radius: 2px;
    overflow: hidden;
  }

  .stat {
    background: var(--bg);
    padding: 40px 32px;
    position: relative;
    transition: background 300ms ease;
  }

  .stat:hover { background: var(--bg-elevated); }

  .stat-number {
    font-family: var(--sans);
    font-size: 52px;
    font-weight: 200;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 16px;
    color: var(--text);
  }

  .stat-label {
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-subtle);
  }

  /* SECTIONS */
  section {
    margin-bottom: 80px;
  }

  .section-head {
    display: flex;
    align-items: baseline;
    gap: 28px;
    margin-bottom: 64px;
    flex-wrap: wrap;
  }

  .section-index {
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    color: var(--text-muted);
  }

  .section-title {
    font-family: var(--sans);
    font-size: clamp(28px, 4vw, 42px);
    font-weight: 200;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: var(--text);
    flex: 1;
  }

  .section-title em {
    font-style: italic;
    color: var(--text-subtle);
  }

  /* TASKS */
  .tasks {
    border: 1px solid var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .task {
    display: grid;
    grid-template-columns: 60px 1fr auto;
    gap: 40px;
    align-items: center;
    padding: 36px 40px;
    border-bottom: 1px solid var(--border);
    transition: background 300ms ease;
    cursor: default;
  }

  .task:last-child { border-bottom: none; }

  .task:hover { background: var(--bg-elevated); }

  .task-num {
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 0.05em;
  }

  .task-body h3 {
    font-family: var(--sans);
    font-size: 22px;
    font-weight: 300;
    letter-spacing: -0.02em;
    margin-bottom: 10px;
    color: var(--text);
  }

  .task-body p {
    font-size: 15px;
    color: var(--text-dim);
    max-width: 560px;
    line-height: 1.6;
    font-weight: 300;
  }

  .task-meta {
    display: flex;
    gap: 20px;
    margin-top: 16px;
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .task-meta span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .task-meta span::before {
    content: '';
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: var(--text-muted);
  }

  .task-badge {
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
    padding: 7px 14px;
    border: 1px solid var(--border-bright);
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    border-radius: 100px;
    white-space: nowrap;
  }

  /* API */
  .endpoints {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .endpoint {
    background: var(--bg);
    padding: 22px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    text-decoration: none;
    color: inherit;
    transition: background 200ms ease;
    border-radius: 0;
  }

  .endpoint:hover { background: var(--bg-elevated); }

  .endpoint-left {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
  }

  .method {
    font-family: var(--mono);
    font-size: 9px;
    font-weight: 600;
    padding: 4px 9px;
    letter-spacing: 0.08em;
    border-radius: 3px;
    text-transform: uppercase;
    flex-shrink: 0;
  }

  .method.get {
    background: rgba(34, 211, 238, 0.1);
    color: var(--cyan);
    border: 1px solid rgba(34, 211, 238, 0.2);
  }

  .method.post {
    background: rgba(255, 107, 53, 0.1);
    color: var(--accent);
    border: 1px solid rgba(255, 107, 53, 0.2);
  }

  .path {
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 400;
    color: var(--text);
  }

  .endpoint-desc {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-subtle);
    letter-spacing: 0.02em;
  }

  /* CODE BLOCK */
  .code-wrap {
    border: 1px solid var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .code-header {
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border);
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-subtle);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .code-dots {
    display: flex;
    gap: 6px;
  }

  .code-dots span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--border-bright);
  }

  pre.code {
    background: var(--bg);
    padding: 28px 32px;
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.75;
    color: var(--text-dim);
    overflow-x: auto;
    margin: 0;
    font-weight: 400;
  }

  .code .c { color: var(--text-muted); font-style: italic; }
  .code .s { color: var(--cyan); }
  .code .k { color: var(--accent); }
  .code .f { color: var(--text); }

  /* RESULTS */
  .results-headline {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 40px;
  }
  .result-cell {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 24px;
    background: var(--bg-card, rgba(255, 255, 255, 0.02));
  }
  .result-num {
    font-size: 36px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -0.02em;
    line-height: 1.1;
  }
  .result-label {
    margin-top: 8px;
    color: var(--text-dim);
    font-size: 13px;
    letter-spacing: 0.02em;
  }
  .result-plots {
    display: grid;
    grid-template-columns: 1fr;
    gap: 32px;
    margin-bottom: 40px;
  }
  .result-plots figure {
    margin: 0;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    background: #000;
  }
  .result-plots img {
    display: block;
    width: 100%;
    height: auto;
  }
  .result-plots figcaption {
    padding: 12px 18px;
    color: var(--text-dim);
    font-size: 13px;
    border-top: 1px solid var(--border);
  }

  @media (max-width: 760px) {
    .results-headline { grid-template-columns: 1fr; }
  }

  /* FOOTER */
  footer {
    margin-top: 40px;
    padding-top: 60px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 40px;
    flex-wrap: wrap;
  }

  .footer-left {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .footer-brand {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 500;
    color: var(--text);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .footer-tagline {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-subtle);
    letter-spacing: 0.04em;
  }

  .footer-links {
    display: flex;
    gap: 32px;
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  .footer-links a {
    color: var(--text-dim);
    text-decoration: none;
    transition: color 200ms ease;
  }

  .footer-links a:hover { color: var(--text); }

  /* RESPONSIVE */
  @media (max-width: 820px) {
    .container { padding: 40px 24px 80px; }
    nav { padding-bottom: 80px; }
    .nav-links { gap: 20px; }
    .hero { padding-bottom: 100px; }
    .hero h1 { font-size: clamp(38px, 10vw, 60px); }
    .hero p { font-size: 17px; }
    .thesis { grid-template-columns: 1fr; gap: 24px; padding: 40px 0; margin-bottom: 80px; }
    .thesis-body { font-size: 18px; }
    .stats { grid-template-columns: repeat(2, 1fr); margin-bottom: 100px; }
    .endpoints { grid-template-columns: 1fr; }
    .task { grid-template-columns: 1fr; gap: 20px; padding: 28px 24px; }
    .task-badge { justify-self: start; }
    section { margin-bottom: 100px; }
    .section-head { margin-bottom: 40px; }
    pre.code { padding: 20px; font-size: 12px; }
    footer { flex-direction: column; gap: 24px; }
  }

  @media (max-width: 520px) {
    .stats { grid-template-columns: 1fr; }
    .hero-cta { flex-direction: column; }
    .btn { justify-content: center; }
  }
</style>
</head>
<body>
  <div class="ambient"></div>
  <div class="container">

    <nav>
      <div class="brand">
        <span class="brand-mark"></span>
        SECUREREVIEW <span class="nav-version">v1.0.0</span>
      </div>
      <div class="nav-links">
        <a href="#tasks">Tasks</a>
        <a href="#results">Results</a>
        <a href="#resources">Resources</a>
        <a href="#api">API</a>
        <a href="https://huggingface.co/spaces/sam25kat/securereview/blob/main/BLOG.md">Blog ↗</a>
        <a href="https://github.com/sam25kat/Secure_Reveiw">GitHub ↗</a>
      </div>
    </nav>

    <section class="hero">
      <div class="eyebrow">The Agent Review Benchmark · Built for the Meta × Hugging Face OpenEnv Hackathon, India 2026 · by ~The Cook House</div>
      <h1>Security review,<br><em>for the age of AI.</em></h1>
      <p><strong>AI writes the code. Who reviews it?</strong> SecureReview is the first OpenEnv harness that trains and grades agents on real security review — supply chain, infrastructure-as-code, and database migrations.</p>
      <div class="hero-cta">
        <a class="btn primary" href="#results">See Training Results <span class="btn-arrow">→</span></a>
        <a class="btn" href="#tasks">View Benchmark</a>
        <a class="btn" href="https://huggingface.co/spaces/sam25kat/securereview/blob/main/BLOG.md">Read the Blog ↗</a>
      </div>
    </section>

    <div class="stats">
      <div class="stat">
        <div class="stat-number">3</div>
        <div class="stat-label">Review Domains</div>
      </div>
      <div class="stat">
        <div class="stat-number">76</div>
        <div class="stat-label">Scenarios</div>
      </div>
      <div class="stat">
        <div class="stat-number">430</div>
        <div class="stat-label">Vulnerabilities</div>
      </div>
      <div class="stat">
        <div class="stat-number">+0.24</div>
        <div class="stat-label">Mean Lift After Training</div>
      </div>
    </div>

    <section id="results">
      <div class="section-head">
        <div class="section-index">01 / RESULTS</div>
        <h2 class="section-title">SFT → GRPO hybrid training. <em>Real lift on every domain.</em></h2>
      </div>
      <div class="results-headline">
        <div class="result-cell"><div class="result-num">+0.302</div><div class="result-label">Dependency · 20/24 wins · 0.083 → 0.385</div></div>
        <div class="result-cell"><div class="result-num">+0.295</div><div class="result-label">Migration · 10/12 wins · 0.170 → 0.465</div></div>
        <div class="result-cell"><div class="result-num">+0.126</div><div class="result-label">IaC · 6/13 wins · 0.177 → 0.303</div></div>
      </div>
      <div class="result-plots">
        <figure>
          <img src="https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/dep/before_after.png" alt="Dependency review — before vs after SFT" />
          <figcaption>Dependency · 24 scenarios. Standout: dep_015 0.02 → 0.93.</figcaption>
        </figure>
        <figure>
          <img src="https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/migration/before_after.png" alt="Migration review — before vs after SFT" />
          <figcaption>Migration · 12 curriculum-filtered scenarios. Standout: migration_025 0.06 → 0.64.</figcaption>
        </figure>
        <figure>
          <img src="https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/iac/before_after.png" alt="IaC review — before vs after SFT" />
          <figcaption>IaC · 13 scenarios. Standout: iac_010 0.01 → 0.76.</figcaption>
        </figure>
      </div>
    </section>

    <section id="tasks">
      <div class="section-head">
        <div class="section-index">02 / BENCHMARK</div>
        <h2 class="section-title">Three domains, three difficulties, <em>one standard.</em></h2>
      </div>
      <div class="tasks">
        <div class="task">
          <div class="task-num">I.</div>
          <div class="task-body">
            <h3>Dependency &amp; Supply Chain Security</h3>
            <p>Typosquats, hallucinated PyPI imports, pinned CVEs. Supply-chain literacy.</p>
            <div class="task-meta">
              <span>24 Scenarios</span>
              <span>15 Steps</span>
              <span>120 Findings</span>
            </div>
          </div>
          <div class="task-badge">Easy</div>
        </div>
        <div class="task">
          <div class="task-num">II.</div>
          <div class="task-body">
            <h3>Infrastructure-as-Code Misconfiguration</h3>
            <p>CIS violations in Terraform / K8s — public buckets, wildcard IAM, privileged containers. Multi-file cloud reasoning.</p>
            <div class="task-meta">
              <span>24 Scenarios</span>
              <span>25 Steps</span>
              <span>155 Findings</span>
            </div>
          </div>
          <div class="task-badge">Medium</div>
        </div>
        <div class="task">
          <div class="task-num">III.</div>
          <div class="task-body">
            <h3>Database Migration Safety</h3>
            <p>SQL migrations against live production context — table sizes, write throughput, downstream services. Judgment, not lint.</p>
            <div class="task-meta">
              <span>28 Scenarios</span>
              <span>35 Steps</span>
              <span>155 Findings</span>
            </div>
          </div>
          <div class="task-badge">Hard</div>
        </div>
      </div>
    </section>

    <div class="thesis">
      <div class="thesis-label">— Thesis</div>
      <div class="thesis-body">
        AI now authors a generation of production code. <span class="muted">Review&nbsp;is&nbsp;the bottleneck&nbsp;— not&nbsp;authorship.</span> <strong>An agent that cannot review code at the level of a senior engineer cannot be trusted to write it.</strong>
      </div>
    </div>

    <section id="resources">
      <div class="section-head">
        <div class="section-index">03 / RESOURCES</div>
        <h2 class="section-title">Everything in one place. <em>For judges &amp; replicators.</em></h2>
      </div>
      <div class="endpoints">
        <a class="endpoint" href="https://huggingface.co/spaces/sam25kat/securereview/blob/main/BLOG.md" target="_blank">
          <div class="endpoint-left"><span class="method get">BLOG</span><span class="path">BLOG.md</span></div>
          <span class="endpoint-desc">submission writeup ↗</span>
        </a>
        <a class="endpoint" href="https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/RESULTS.md" target="_blank">
          <div class="endpoint-left"><span class="method get">DOC</span><span class="path">RESULTS.md</span></div>
          <span class="endpoint-desc">full training story ↗</span>
        </a>
        <a class="endpoint" href="https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/SCENARIOS.md" target="_blank">
          <div class="endpoint-left"><span class="method get">DOC</span><span class="path">SCENARIOS.md</span></div>
          <span class="endpoint-desc">all 76 scenarios indexed ↗</span>
        </a>
        <a class="endpoint" href="https://huggingface.co/spaces/sam25kat/securereview/tree/main/training_results/plots" target="_blank">
          <div class="endpoint-left"><span class="method get">PLOTS</span><span class="path">/training_results/plots</span></div>
          <span class="endpoint-desc">PNGs + results.json ↗</span>
        </a>
        <a class="endpoint" href="https://huggingface.co/spaces/sam25kat/securereview-trainer" target="_blank">
          <div class="endpoint-left"><span class="method post">RUN</span><span class="path">securereview-trainer</span></div>
          <span class="endpoint-desc">dependency · one-click ↗</span>
        </a>
        <a class="endpoint" href="https://huggingface.co/spaces/sam25kat/securereview-trainer-migration" target="_blank">
          <div class="endpoint-left"><span class="method post">RUN</span><span class="path">securereview-trainer-migration</span></div>
          <span class="endpoint-desc">migration · one-click ↗</span>
        </a>
        <a class="endpoint" href="https://huggingface.co/spaces/sam25kat/securereview-trainer-iac" target="_blank">
          <div class="endpoint-left"><span class="method post">RUN</span><span class="path">securereview-trainer-iac</span></div>
          <span class="endpoint-desc">iac · one-click ↗</span>
        </a>
        <a class="endpoint" href="https://github.com/sam25kat/Secure_Reveiw" target="_blank">
          <div class="endpoint-left"><span class="method get">CODE</span><span class="path">github.com/sam25kat/Secure_Reveiw</span></div>
          <span class="endpoint-desc">full source ↗</span>
        </a>
        <a class="endpoint" href="/docs" target="_blank">
          <div class="endpoint-left"><span class="method get">API</span><span class="path">OpenAPI / Swagger</span></div>
          <span class="endpoint-desc">interactive docs ↗</span>
        </a>
      </div>
    </section>

    <section id="api">
      <div class="section-head">
        <div class="section-index">04 / OPENENV INTERFACE</div>
        <h2 class="section-title">Standard gym-style endpoints. <em>Plus a six-line quickstart.</em></h2>
      </div>
      <div class="endpoints" style="margin-bottom: 28px;">
        <a class="endpoint" href="/health"><div class="endpoint-left"><span class="method get">GET</span><span class="path">/health</span></div><span class="endpoint-desc">health</span></a>
        <a class="endpoint" href="/tasks"><div class="endpoint-left"><span class="method get">GET</span><span class="path">/tasks</span></div><span class="endpoint-desc">list tasks</span></a>
        <a class="endpoint" href="/metadata"><div class="endpoint-left"><span class="method get">GET</span><span class="path">/metadata</span></div><span class="endpoint-desc">metadata</span></a>
        <a class="endpoint" href="/docs"><div class="endpoint-left"><span class="method get">GET</span><span class="path">/docs</span></div><span class="endpoint-desc">openapi</span></a>
        <div class="endpoint"><div class="endpoint-left"><span class="method post">POST</span><span class="path">/reset</span></div><span class="endpoint-desc">start episode</span></div>
        <div class="endpoint"><div class="endpoint-left"><span class="method post">POST</span><span class="path">/step</span></div><span class="endpoint-desc">execute action</span></div>
      </div>
      <div class="code-wrap">
        <div class="code-header">
          <div class="code-dots"><span></span><span></span><span></span></div>
          <span>terminal — full episode in 6 lines</span>
        </div>
<pre class="code"><span class="c"># 1. start a dependency review episode</span>
<span class="f">curl</span> -X POST <span class="s">https://sam25kat-securereview.hf.space/reset</span> \\
  -d <span class="s">'{"task_id": "dependency_review"}'</span>

<span class="c"># 2. mark complete to receive the F1-graded reward</span>
<span class="f">curl</span> -X POST <span class="s">https://sam25kat-securereview.hf.space/step</span> \\
  -d <span class="s">'{"action": {"action_type": "mark_complete"}}'</span></pre>
      </div>
    </section>

    <footer>
      <div class="footer-left">
        <div class="footer-brand">SECUREREVIEW × TEAM COOKHOUSE</div>
        <div class="footer-tagline">Meta × Hugging Face OpenEnv Hackathon · India 2026</div>
      </div>
      <div class="footer-links">
        <a href="https://github.com/sam25kat/Secure_Reveiw">GitHub ↗</a>
        <a href="https://huggingface.co/spaces/sam25kat/securereview/tree/main">Source ↗</a>
        <a href="https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/RESULTS.md">Results ↗</a>
        <a href="https://huggingface.co/spaces/sam25kat/securereview/blob/main/BLOG.md">Blog ↗</a>
        <a href="/docs">API ↗</a>
      </div>
    </footer>

  </div>
</body>
</html>"""
