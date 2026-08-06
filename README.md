<p align="center">
  <img src="static/icons/icon-192.png" alt="Void" width="96">
</p>

<p align="center">
  A self-hosted AI workspace for chat, agents, research, documents, email, notes, calendar, and local model workflows.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="docs/setup.md">Setup Guide</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="ROADMAP.md">Roadmap</a>
</p>


---

## What is Void?

Void is a self-hosted, local-first AI workspace. Chat with agents, run deep web research, write documents, and manage email, notes, tasks, and a calendar — with your own models, your own data, and no cloud dependency. Auth is on by default, everything runs on your machine, and optional services (model serving, embeddings, web search) are pluggable and degrade gracefully.

Built with Python/FastAPI and a dependency-free vanilla-JS frontend. The detailed install, GPU, HTTPS, and troubleshooting notes live in the [setup guide](docs/setup.md); this page is the front door.

## Quick Start

> `dev` is the default branch and gets the newest changes first. Use [`main`](https://github.com/pewdiepie-archdaemon/void/tree/main) if you want the more curated branch.

Defaults work out of the box: clone, run, then configure models, search, and email inside **Settings**. Only edit `.env` for deployment-level overrides such as `APP_BIND`, `APP_PORT`, `AUTH_ENABLED`, or `DATABASE_URL`.

On first setup, Void creates an admin account (`admin` unless `VOID_ADMIN_USER` is set) and prints a temporary password in the terminal. For Docker, the same line appears in `docker compose logs void`. Use it for the first login, then change it in **Settings**.

### 🐳 Docker (recommended)

```bash
git clone https://github.com/pewdiepie-archdaemon/void.git
cd void
cp .env.example .env       # optional, but recommended for explicit defaults
docker compose up -d --build
```

Open `http://localhost:7000` when the containers are healthy. Compose also starts ChromaDB (vector store), SearXNG (web search), and ntfy (notifications). The first admin password is printed in `docker compose logs void`.

To pass an NVIDIA/AMD GPU into the container for Cookbook model serving, follow the GPU overlay instructions in the [setup guide](docs/setup.md). On Apple Silicon, Docker cannot reach the Metal GPU — run natively instead (below).

### 🪟 Windows (native, no Docker)

One command — creates a venv, installs dependencies, runs first-time setup, and starts the server. Safe to re-run:

```powershell
git clone https://github.com/pewdiepie-archdaemon/void.git
cd void
powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
```

Requires Python 3.11+. The core app (chat, agents, memory, documents, email, calendar, deep research) runs fully native. For full **Cookbook** background model downloads and the agent shell tool, also install [Git for Windows](https://git-scm.com/download/win). For a local model, [Ollama](https://ollama.com/download) is the easiest path — add `http://localhost:11434/v1` in Settings. Open `http://localhost:7000` and log in with the generated admin password.

### 🍎 macOS (native, Apple Silicon)

```bash
git clone https://github.com/pewdiepie-archdaemon/void.git
cd void
./start-macos.sh
```

Installs Homebrew dependencies (Python, tmux, llama.cpp), creates the venv, and starts the server at `http://127.0.0.1:7860` (port `7000` is usually held by AirPlay Receiver on macOS). Runs on the Metal GPU — Docker can't. `VOID_HOST=0.0.0.0 ./start-macos.sh` exposes it on your LAN/Tailscale.

### 🐧 Native Linux

```bash
git clone https://github.com/pewdiepie-archdaemon/void.git
cd void
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py
python -m uvicorn app:app --host 127.0.0.1 --port 7000
```

Requires Python 3.11+. Cookbook also needs `tmux` for background model downloads and serves. The app itself is lightweight; local model serving is the heavy part and depends on your hardware — small hosts can connect to API or remote model servers instead.

> **Changing port/bind:** `APP_BIND`, `APP_PORT`, `AUTH_ENABLED`, and every other environment variable are documented in the [setup guide](docs/setup.md#configuration).

## Features

- **Chat + Agents** — local or API models, tools, MCP servers, file attachments, shell access, skills, and persistent memory.
- **Cookbook** — hardware-aware model recommendations, downloads, and local serving (llama.cpp, vLLM, SGLang, Ollama) with GPU support.
- **Deep Research** — multi-step web research with source reading and report generation.
- **Compare** — blind side-by-side model testing and synthesis.
- **Documents** — writing-first editor with AI edits, suggestions, Markdown, HTML, CSV, and syntax highlighting.
- **Email** — IMAP/SMTP inbox with triage, tags, summaries, reminders, and reply drafts.
- **Notes, Tasks + Calendar** — reminders, todos, scheduled agent tasks, and CalDAV sync.
- **Contacts** — CardDAV address book, fed from email senders and documents.
- **Vault** — encrypted storage for credentials and secrets.
- **Automation** — webhooks, scoped API tokens, and scheduled tasks with session delivery.
- **Integrations** — MCP, GitHub Copilot and ChatGPT Subscription device-flow sign-in, and Codex/Claude agent endpoints.
- **Speech** — text-to-speech, plus local speech-to-text (faster-whisper).
- **Extras** — gallery with image editor, signature stamps, personal-docs RAG, themes, uploads, web search, presets, sessions, and 2FA.

## Demo

A full hover-to-play tour lives on the landing page: [`docs/index.html`](docs/index.html).

## Documentation

- [Setup Guide](docs/setup.md) — detailed install, GPU notes, HTTPS, troubleshooting, configuration reference
- [Backup & Restore](docs/backup-restore.md) — backing up and restoring everything in `data/`
- [Outlook / Office 365 email](docs/email-outlook.md) — current IMAP/SMTP limitation and planned direction
- [Contributing](CONTRIBUTING.md) — setup, testing, and pull request guidelines
- [Roadmap](ROADMAP.md)

## Security

Void is a self-hosted workspace with powerful local tools: shell access, file uploads, model downloads, web research, email/calendar integrations, and API tokens. Treat it like an admin console.

- Keep `AUTH_ENABLED=true` for any network-accessible deployment and `LOCALHOST_BYPASS=false` outside local development.
- Bind to loopback by default; bind to `0.0.0.0` only on a trusted LAN/VPN such as Tailscale, ideally behind HTTPS.
- Keep `.env`, `data/`, `logs/`, uploads, backups, and databases out of Git and private shares (ignored by default).
- See the [security notes](docs/setup.md#security-notes) for the full checklist.

## Star History

<a href="https://www.star-history.com/?repos=pewdiepie-archdaemon%2Fvoid&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=pewdiepie-archdaemon/void&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=pewdiepie-archdaemon/void&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=pewdiepie-archdaemon/void&type=Date" />
 </picture>
</a>

## License

AGPL-3.0-or-later — see [LICENSE](LICENSE) and [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md).
