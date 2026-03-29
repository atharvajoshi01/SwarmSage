# SwarmSage

A universal swarm intelligence engine that predicts real-world outcomes through multi-agent simulation.

Upload any document, and SwarmSage automatically extracts entities, builds a knowledge graph, generates AI agent personas, simulates social interactions on Twitter/Reddit-like platforms, and produces detailed analysis reports.

## How It Works

SwarmSage operates as a 5-step pipeline:

| Step | Name | Description |
|------|------|-------------|
| 01 | **Graph Building** | Upload documents (PDF/MD/TXT) → LLM extracts entities & relationships → builds a knowledge graph via Zep |
| 02 | **Environment Setup** | Graph entities become AI agent personas with personality, MBTI, profession, interests, etc. |
| 03 | **Run Simulation** | Agents interact on simulated Twitter & Reddit platforms via the OASIS engine |
| 04 | **Report Generation** | A ReACT agent analyzes simulation results using search, analytics, and interview tools |
| 05 | **Deep Interaction** | Chat with any individual agent or the report agent for follow-up Q&A |

## Tech Stack

- **Backend**: Flask (Python 3.11+)
- **Frontend**: Vue 3 + Vite + D3.js
- **LLM**: Any OpenAI-compatible API (GPT-4o-mini, Qwen-plus, etc.)
- **Knowledge Graph**: Zep Cloud (GraphRAG)
- **Simulation Engine**: OASIS by CAMEL-AI
- **Package Manager**: uv (Python), npm (Node.js)

## Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- An OpenAI-compatible LLM API key
- A [Zep Cloud](https://app.getzep.com/) API key (free tier available)

## Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/atharvajoshi01/SwarmSage.git
cd SwarmSage
cp .env.example .env
# Edit .env with your API keys
```

### 2. Install dependencies

```bash
npm run setup:all
```

This installs Node.js dependencies (root + frontend) and Python dependencies (backend via uv).

### 3. Run

```bash
npm run dev
```

This starts both the backend (port 5001) and frontend (port 3000) concurrently.

Open http://localhost:3000 in your browser.

### Docker

```bash
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

## Configuration

All configuration is via the `.env` file in the project root:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_KEY` | Yes | - | Your LLM API key |
| `LLM_BASE_URL` | No | `https://api.openai.com/v1` | OpenAI-compatible API endpoint |
| `LLM_MODEL_NAME` | No | `gpt-4o-mini` | Model to use |
| `ZEP_API_KEY` | Yes | - | Zep Cloud API key |
| `OASIS_DEFAULT_MAX_ROUNDS` | No | `10` | Max simulation rounds |
| `REPORT_AGENT_MAX_TOOL_CALLS` | No | `5` | Max tool calls per report section |
| `FLASK_DEBUG` | No | `True` | Enable Flask debug mode |

## Project Structure

```
SwarmSage/
├── backend/
│   ├── app/
│   │   ├── api/              # Flask API routes (graph, simulation, report)
│   │   ├── services/         # Core business logic
│   │   ├── models/           # Data models (Project, Task)
│   │   ├── utils/            # Utilities (LLM client, file parser, retry)
│   │   └── config.py         # Configuration management
│   ├── tests/                # Pytest test suite
│   ├── run.py                # Backend entry point
│   └── pyproject.toml        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── views/            # Vue page components
│   │   ├── components/       # Reusable Vue components
│   │   ├── api/              # Axios API client
│   │   ├── router/           # Vue Router config
│   │   └── store/            # State management
│   └── package.json
├── .env.example              # Environment template
├── docker-compose.yml        # Docker deployment
├── Dockerfile
└── package.json              # Root monorepo config
```

## Running Tests

```bash
cd backend
uv run pytest tests/ -v
```

## API Endpoints

### Graph Building
- `POST /api/graph/upload` - Upload files & extract text
- `POST /api/graph/ontology` - Generate ontology from text
- `POST /api/graph/build` - Build knowledge graph
- `GET /api/graph/task-status/<task_id>` - Check build progress

### Simulation
- `POST /api/simulation/create` - Initialize simulation
- `POST /api/simulation/prepare` - Generate profiles & config
- `GET /api/simulation/prepare/status` - Check preparation progress
- `POST /api/simulation/start` - Start simulation
- `POST /api/simulation/stop` - Stop running simulation
- `GET /api/simulation/<id>/run-status` - Get live status
- `GET /api/simulation/<id>/posts` - Retrieve simulation posts
- `POST /api/simulation/interview/batch` - Interview agents

### Report
- `POST /api/report/generate` - Generate analysis report
- `GET /api/report/generate/status` - Check report progress
- `GET /api/report/<report_id>` - Get completed report
- `POST /api/report/chat` - Chat with report agent

## Author

**Atharva Joshi** - [GitHub](https://github.com/atharvajoshi01)

## License

MIT
