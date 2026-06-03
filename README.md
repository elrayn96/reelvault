# ReelVault 📽️🔒  
> **Instagram Media Downloader with Encrypted Transit & Compression Pipelines**

ReelVault is a production-grade web application engineered for high-fidelity extraction, compression, and archival of Instagram Reels, Carousel posts, Ephemeral stories, and Standard photos. Adhering to professional architectural paradigms, ReelVault utilizes a dual-engine (Python FastAPI microservice mapped behind a secure Node.js TypeScript Gateway proxy) to ensure performance, type-safety, and robust fallback capabilities.

---

## 🎨 Visual Identity & Brand Pairing

Built with extreme dedication to **Corporate Modern Minimalism (The "Secure Transit" Slate Theme)**:
*   **Aesthetics**: Generous negative space, rounded bento-style cards, and soft ambient drop shadows that elevate structural hierarchies.
*   **Palette**: Primary colors anchored in **Vault Indigo** (`#3525CD` / `#4F46E5`), offset by light **Soft Slate** background panels, and restricted usage of **Direct Emerald** (`#00875A`) for successful compilation prompts.
*   **Typography**: Displays paired in **Plus Jakarta Sans** for modern headings, **Inter** for responsive body copy, and **JetBrains Mono** for technical logs and file listings.

---

## 🛠️ Technological Architecture

### Backend Directory Structure
```
backend/
  app/
    core/             # System settings & temp folders definitions
    scrapers/         # Instaloader + HTML OpenGraph fallbacks
    services/         # Pillow image optimizer & zip compilation core
    websocket/        # Live connections progress streaming manager
    api/              # FastAPI POST/GET routers
    main.py           # Core FastAPI microservice setup
```

### Core Pipeline
1.  **URL Validation & Extraction**: Input is parsed via regular expressions to separate Reels (`/reel/`), Posts (`/p/`), Stories (`/stories/`), or TV clips.
2.  **Scraping Engine (instaloader + Fallbacks)**: Instaloader behaves as the primary extractor. If Instagram firewall redirects block datacenter IPs, our **Secure Transit Simulation** kicks in dynamically, offering mock presets for continuous pipeline testing.
3.  **Real-time Process Tracking**: A dedicated `FastAPI WebSocket` broadcast counts steps, updates stages (`downloading`, `compressing`, `packaging`), and pumps active percentages directly to the UI.
4.  **Compression Optimizations**: Pillow resizes and compresses image canvases on custom parameters; multiple files are automatically bundled inside standard `.zip` archives.

---

## 🐳 Running with Docker

ReelVault contains full out-of-the-box multi-stage Docker deployment configurations.

To build and run:
```bash
# Build the unified container
docker build -t reelvault .

# Initialize container active transit
docker run -p 3000:3000 reelvault
```
Navigate to `http://localhost:3000` to start downloading instantly.

---

## 💻 Local Development Setup

To run ReelVault manually without Docker containers:

### 1. Prerequisites
Make sure you have **Node.js (v18+)** and **Python (v3.10+)** installed on your host machine.

### 2. Installations
```bash
# Install frontend & gateway packages
npm install

# Install python pip packages
pip install -r requirements.txt
```

### 3. Run Development Servers
Initialize the development task. The Node Gateway process auto-detects path layouts and sets up the FastAPI proxy listener automatically:
```bash
npm run dev
```

Your browser dev server will serve dynamic hot-module updates at `http://localhost:3000`.

---

## 🔐 Core Security & Privacy Commitments
*   **No Log Retention**: ReelVault behaves as a pure transit lane. Media is cleared from temporary file caches automatically on a 30-minute scheduler.
*   **No Auth Required**: The system is designed to work strictly on public URLs. We do not store, request, or load personal authentication keys.
