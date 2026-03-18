<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>VOID — AI Screen Assistant</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=IBM+Plex+Mono:wght@300;400;600&display=swap" rel="stylesheet"/>
<style>
:root {
  --cyan: #00aaff;
  --cyan-dim: #0066aa;
  --cyan-glow: rgba(0,170,255,0.15);
  --bg: #010d1a;
  --bg2: #020f1f;
  --bg3: #031424;
  --text: #b0d8f0;
  --text-dim: #4a7a9b;
  --border: rgba(0,170,255,0.2);
  --border-bright: rgba(0,170,255,0.5);
}

* { margin:0; padding:0; box-sizing:border-box; }

html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 14px;
  line-height: 1.7;
  overflow-x: hidden;
}

/* Scanlines */
body::before {
  content: '';
  position: fixed; inset: 0; z-index: 9999; pointer-events: none;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0px, transparent 3px,
    rgba(0,170,255,0.012) 3px, rgba(0,170,255,0.012) 4px
  );
}

/* Grid background */
body::after {
  content: '';
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(0,170,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,170,255,0.04) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* ─── HERO ─────────────────────────────────────────────── */
#hero {
  position: relative; z-index: 1;
  min-height: 100vh;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  overflow: hidden;
  padding: 60px 24px 40px;
}

#hero-canvas {
  position: absolute; inset: 0; z-index: 0;
  opacity: 0.9;
}

.hero-content {
  position: relative; z-index: 2;
  text-align: center;
}

.void-wordmark {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(52px, 10vw, 100px);
  font-weight: 900;
  color: var(--cyan);
  letter-spacing: 24px;
  text-shadow: 0 0 40px rgba(0,170,255,0.7), 0 0 80px rgba(0,170,255,0.3);
  animation: flicker 8s infinite;
  margin-bottom: 8px;
}

@keyframes flicker {
  0%,95%,100% { opacity: 1; }
  96% { opacity: 0.85; }
  97% { opacity: 1; }
  98% { opacity: 0.9; }
}

.hero-sub {
  font-family: 'Share Tech Mono', monospace;
  font-size: clamp(11px, 2vw, 14px);
  color: var(--cyan-dim);
  letter-spacing: 6px;
  text-transform: uppercase;
  margin-bottom: 20px;
}

.hero-tagline {
  font-size: 13px;
  color: var(--text-dim);
  max-width: 560px;
  margin: 0 auto 40px;
  letter-spacing: 0.5px;
  border-left: 2px solid var(--cyan-dim);
  padding-left: 16px;
  text-align: left;
}

.hero-badges {
  display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
  margin-bottom: 48px;
}

.badge {
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  letter-spacing: 2px;
  padding: 4px 12px;
  border: 1px solid var(--border-bright);
  color: var(--cyan);
  background: rgba(0,170,255,0.05);
  text-transform: uppercase;
}

.scroll-hint {
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  letter-spacing: 3px;
  color: var(--text-dim);
  animation: bob 2s ease-in-out infinite;
}
.scroll-hint::after { content: ' ▼'; }
@keyframes bob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(6px)} }

/* ─── NAV ──────────────────────────────────────────────── */
nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(1,13,26,0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 0;
  padding: 0 24px;
  overflow-x: auto;
}

nav a {
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--text-dim);
  text-decoration: none;
  padding: 14px 18px;
  border-right: 1px solid var(--border);
  white-space: nowrap;
  transition: color .2s, background .2s;
}
nav a:first-child { border-left: 1px solid var(--border); }
nav a:hover { color: var(--cyan); background: var(--cyan-glow); }

.nav-logo {
  font-family: 'Orbitron', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 6px;
  padding: 14px 24px 14px 0;
  margin-right: auto;
  flex-shrink: 0;
}

/* ─── LAYOUT ───────────────────────────────────────────── */
.page {
  position: relative; z-index: 1;
  max-width: 980px;
  margin: 0 auto;
  padding: 0 24px 80px;
}

/* ─── SECTION ──────────────────────────────────────────── */
section {
  margin-top: 80px;
}

.section-label {
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  letter-spacing: 4px;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-bottom: 8px;
}
.section-label::before { content: '// '; color: var(--cyan-dim); }

h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(18px, 3vw, 26px);
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 4px;
  text-transform: uppercase;
  margin-bottom: 28px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin: 32px 0 12px;
}

p { color: var(--text); margin-bottom: 16px; }

/* ─── FEATURE GRID ─────────────────────────────────────── */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  margin-bottom: 8px;
}

.feature-card {
  background: var(--bg2);
  padding: 20px;
  transition: background .2s;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), transparent);
  transform: translateX(-100%);
  transition: transform .4s;
}

.feature-card:hover { background: var(--bg3); }
.feature-card:hover::before { transform: translateX(0); }

.feature-icon {
  font-size: 20px;
  margin-bottom: 10px;
  display: block;
}

.feature-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--cyan);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.feature-desc {
  font-size: 12px;
  color: var(--text-dim);
  line-height: 1.5;
}

/* ─── TABLES ───────────────────────────────────────────── */
.tbl-wrap { overflow-x: auto; margin-bottom: 8px; }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
}

thead tr {
  background: rgba(0,170,255,0.08);
  border-bottom: 1px solid var(--border-bright);
}

th {
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--cyan);
  padding: 10px 16px;
  text-align: left;
}

td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  vertical-align: top;
}

tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--cyan-glow); }

td:first-child { color: var(--cyan); font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; }

/* ─── CODE BLOCKS ──────────────────────────────────────── */
pre {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--cyan);
  padding: 20px;
  overflow-x: auto;
  margin: 16px 0;
  position: relative;
}

pre::before {
  content: attr(data-lang);
  position: absolute; top: 8px; right: 12px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 9px;
  letter-spacing: 2px;
  color: var(--text-dim);
  text-transform: uppercase;
}

code {
  font-family: 'Share Tech Mono', monospace;
  font-size: 12.5px;
  color: var(--cyan);
  line-height: 1.6;
}

p code, td code, li code {
  background: rgba(0,170,255,0.08);
  border: 1px solid var(--border);
  padding: 1px 6px;
  font-size: 12px;
  color: var(--cyan);
}

/* ─── ARCH TREE ────────────────────────────────────────── */
.arch-tree {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--cyan);
  padding: 24px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 12.5px;
  line-height: 1.9;
  color: var(--text);
  white-space: pre;
  overflow-x: auto;
}

.arch-tree .dir  { color: var(--cyan); }
.arch-tree .file { color: var(--text-dim); }
.arch-tree .comment { color: #2a5a7a; }

/* ─── SETUP STEPS ──────────────────────────────────────── */
.steps { counter-reset: step; }

.step {
  display: flex; gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border);
}

.step:last-child { border-bottom: none; }

.step-num {
  font-family: 'Orbitron', sans-serif;
  font-size: 28px;
  font-weight: 900;
  color: var(--border-bright);
  min-width: 48px;
  line-height: 1;
  padding-top: 2px;
  flex-shrink: 0;
}

.step-body { flex: 1; }

.step-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--cyan);
  text-transform: uppercase;
  margin-bottom: 10px;
}

/* ─── API ROUTE PILLS ──────────────────────────────────── */
.method {
  display: inline-block;
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 1px;
  padding: 2px 8px;
  margin-right: 4px;
}
.method.post { background: rgba(0,170,255,0.15); color: var(--cyan); border: 1px solid var(--cyan-dim); }
.method.get  { background: rgba(0,200,100,0.1);  color: #00cc66;     border: 1px solid #004422; }

/* ─── ENV TABLE ────────────────────────────────────────── */
.env-key {
  font-family: 'Share Tech Mono', monospace;
  color: #ffcc44;
  font-size: 12px;
}

/* ─── NOTES ────────────────────────────────────────────── */
.notes { display: flex; flex-direction: column; gap: 12px; }

.note {
  display: flex; gap: 14px; align-items: flex-start;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--cyan-dim);
  padding: 14px 16px;
  font-size: 12.5px;
  color: var(--text);
}

.note-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }

/* ─── FOOTER ───────────────────────────────────────────── */
footer {
  position: relative; z-index: 1;
  border-top: 1px solid var(--border);
  text-align: center;
  padding: 40px 24px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--text-dim);
}

footer span { color: var(--cyan); }

/* ─── FLOW DIAGRAM ─────────────────────────────────────── */
.flow {
  display: flex; align-items: center; flex-wrap: wrap; gap: 0;
  margin: 20px 0;
}

.flow-box {
  background: var(--bg2);
  border: 1px solid var(--border-bright);
  padding: 10px 16px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: var(--cyan);
  text-align: center;
  letter-spacing: 1px;
  white-space: nowrap;
}

.flow-arrow {
  font-size: 14px;
  color: var(--cyan-dim);
  padding: 0 8px;
  flex-shrink: 0;
}

/* ─── STACK CARDS ──────────────────────────────────────── */
.stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.stack-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 16px;
  transition: border-color .2s, background .2s;
}

.stack-card:hover {
  border-color: var(--border-bright);
  background: var(--bg3);
}

.stack-layer {
  font-family: 'Share Tech Mono', monospace;
  font-size: 9px;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 6px;
}

.stack-tech {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 1px;
}

.stack-detail {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 4px;
  line-height: 1.4;
}

/* Animated entrance */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.reveal {
  opacity: 0;
  animation: fadeUp .5s ease forwards;
}
</style>
</head>
<body>

<!-- ═══════════════════ HERO ═══════════════════ -->
<section id="hero">
  <canvas id="hero-canvas"></canvas>
  <div class="hero-content reveal" style="animation-delay:.1s">
    <div class="void-wordmark">VOID</div>
    <div class="hero-sub">AI Screen Assistant · V3.0</div>
    <p class="hero-tagline">
      A floating AI desktop assistant that reads your screen,
      understands Telugu, and helps you reply, summarize, translate,
      and draft — powered entirely by local models.
    </p>
    <div class="hero-badges">
      <span class="badge">Qwen2.5-3B · CPU</span>
      <span class="badge">Groq Vision</span>
      <span class="badge">Whisper ASR</span>
      <span class="badge">FastAPI Backend</span>
      <span class="badge">PyQt5 HUD</span>
      <span class="badge">Local-First</span>
    </div>
    <div class="scroll-hint">SCROLL TO EXPLORE</div>
  </div>
</section>

<!-- ═══════════════════ NAV ═══════════════════ -->
<nav>
  <div class="nav-logo">VOID</div>
  <a href="#overview">Overview</a>
  <a href="#features">Features</a>
  <a href="#architecture">Architecture</a>
  <a href="#stack">Stack</a>
  <a href="#setup">Setup</a>
  <a href="#api">API</a>
  <a href="#flow">Flow</a>
  <a href="#env">Config</a>
  <a href="#notes">Notes</a>
</nav>

<div class="page">

<!-- ═══════════════════ OVERVIEW ═══════════════════ -->
<section id="overview">
  <div class="section-label">01 · Overview</div>
  <h2>What Is VOID</h2>
  <p>
    VOID runs as a frameless floating widget on your Windows desktop.
    It uses <code>Qwen2.5-3B</code> (GGUF, CPU-only) for all text tasks
    and <code>Groq Vision</code> for screen understanding.
    No cloud LLM dependency for text generation — everything runs on your machine.
  </p>
  <p>
    Built specifically for Telugu users, VOID understands Tenglish (Telugu + English code-mix)
    and generates contextually appropriate replies for WhatsApp, email, and more —
    without sending a single character of your data to an external LLM.
  </p>
</section>

<!-- ═══════════════════ FEATURES ═══════════════════ -->
<section id="features">
  <div class="section-label">02 · Features</div>
  <h2>Capabilities</h2>

  <div class="feature-grid">
    <div class="feature-card">
      <span class="feature-icon">💬</span>
      <div class="feature-name">WhatsApp Reply</div>
      <div class="feature-desc">Captures the active chat, extracts messages, generates 3 Tenglish reply suggestions via Groq Vision + Qwen.</div>
    </div>
    <div class="feature-card">
      <span class="feature-icon">📸</span>
      <div class="feature-name">Screenshot</div>
      <div class="feature-desc">Saves a timestamped PNG to <code>~/Pictures/VOID/</code> with one tap.</div>
    </div>
    <div class="feature-card">
      <span class="feature-icon">🎙️</span>
      <div class="feature-name">Voice Type</div>
      <div class="feature-desc">Transcribes mic input via Whisper and types it into the active window automatically.</div>
    </div>
    <div class="feature-card">
      <span class="feature-icon">🔍</span>
      <div class="feature-name">Explain Screen</div>
      <div class="feature-desc">Sends a screenshot to Groq Vision (llama-4-scout) for full content explanation and analysis.</div>
    </div>
    <div class="feature-card">
      <span class="feature-icon">🌐</span>
      <div class="feature-name">Translate</div>
      <div class="feature-desc">Extracts and translates on-screen Telugu/Tenglish text to English in-place.</div>
    </div>
    <div class="feature-card">
      <span class="feature-icon">📋</span>
      <div class="feature-name">Summarize</div>
      <div class="feature-desc">Summarizes screen content into concise bullet points using Qwen locally.</div>
    </div>
    <div class="feature-card">
      <span class="feature-icon">📧</span>
      <div class="feature-name">Email Draft</div>
      <div class="feature-desc">Converts a voice note into a structured, professional email with proper formatting.</div>
    </div>
    <div class="feature-card">
      <span class="feature-icon">🤖</span>
      <div class="feature-name">Ask VOID</div>
      <div class="feature-desc">Persistent chat window backed by Qwen2.5-3B for general-purpose queries and assistance.</div>
    </div>
  </div>
</section>

<!-- ═══════════════════ ARCHITECTURE ═══════════════════ -->
<section id="architecture">
  <div class="section-label">03 · Architecture</div>
  <h2>Project Structure</h2>

  <div class="arch-tree"><span class="dir">void/
└── project/
    ├── backend/
    │   ├── </span><span class="file">main.py               </span><span class="comment"># FastAPI app entry point</span>
<span class="dir">    │   ├── </span><span class="file">config.py             </span><span class="comment"># Loads .env, exports constants</span>
<span class="dir">    │   ├── </span><span class="file">database.py           </span><span class="comment"># SQLAlchemy engine + session</span>
<span class="dir">    │   ├── </span><span class="file">models.py             </span><span class="comment"># ORM models (ActionLog, VoiceLog…)</span>
<span class="dir">    │   ├── routers/
    │   │   ├── </span><span class="file">text_router.py        </span><span class="comment"># POST /text/*</span>
<span class="dir">    │   │   ├── </span><span class="file">screen_router.py      </span><span class="comment"># POST /screen/*</span>
<span class="dir">    │   │   └── </span><span class="file">meeting_router.py     </span><span class="comment"># POST /meeting/*, GET /history/*</span>
<span class="dir">    │   └── services/
    │       ├── </span><span class="file">qwen_service.py       </span><span class="comment"># llama-cpp-python Qwen wrapper</span>
<span class="dir">    │       └── </span><span class="file">gemini_service.py     </span><span class="comment"># Groq Vision API client</span>
<span class="dir">    └── frontend/
        └── </span><span class="file">void_ball.py          </span><span class="comment"># PyQt5 floating HUD</span></div>
</section>

<!-- ═══════════════════ STACK ═══════════════════ -->
<section id="stack">
  <div class="section-label">04 · Stack</div>
  <h2>Technology</h2>

  <div class="stack-grid">
    <div class="stack-card">
      <div class="stack-layer">LLM</div>
      <div class="stack-tech">Qwen 2.5-3B</div>
      <div class="stack-detail">Q4_K_M GGUF · llama-cpp-python · CPU only · 4–8 GB RAM</div>
    </div>
    <div class="stack-card">
      <div class="stack-layer">Vision</div>
      <div class="stack-tech">Groq API</div>
      <div class="stack-detail">llama-4-scout-17b-16e-instruct · free tier</div>
    </div>
    <div class="stack-card">
      <div class="stack-layer">ASR</div>
      <div class="stack-tech">Whisper</div>
      <div class="stack-detail">OpenAI Whisper tiny · fully local · sounddevice input</div>
    </div>
    <div class="stack-card">
      <div class="stack-layer">TTS</div>
      <div class="stack-tech">pyttsx3</div>
      <div class="stack-detail">Offline text-to-speech · no API required</div>
    </div>
    <div class="stack-card">
      <div class="stack-layer">Backend</div>
      <div class="stack-tech">FastAPI</div>
      <div class="stack-detail">SQLAlchemy · PostgreSQL · psycopg2 · uvicorn</div>
    </div>
    <div class="stack-card">
      <div class="stack-layer">Frontend</div>
      <div class="stack-tech">PyQt5</div>
      <div class="stack-detail">Frameless floating HUD · pyautogui · Pillow</div>
    </div>
  </div>
</section>

<!-- ═══════════════════ SETUP ═══════════════════ -->
<section id="setup">
  <div class="section-label">05 · Setup</div>
  <h2>Installation</h2>

  <div class="steps">
    <div class="step">
      <div class="step-num">01</div>
      <div class="step-body">
        <div class="step-title">Clone the Repository</div>
        <pre data-lang="bash"><code>git clone https://github.com/MKarthik730/void.git
cd void/project</code></pre>
      </div>
  