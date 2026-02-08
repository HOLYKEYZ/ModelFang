# ModelFang
### Advanced AI Red Teaming & LLM Exploitation Framework

<img src="frontend/public/logo.png" width="128" alt="ModelFang Logo" />

**ModelFang** is an authorized, graph-based adversarial testing framework designed to evaluate the safety and robustness of Large Language Models (LLMs). It automates the generation, execution, and scoring of complex multi-turn jailbreak attacks.

---

## 🔥 Proof of Concept: Successful Jailbreak

ModelFang successfully jailbroke **Llama 3.3 70B** and **Gemini 2.5 Pro** in just **2 turns** using Auto-LLM mode:

| Attacker Prompt | Target Response (Jailbroken) |
|:---:|:---:|
| ![Attacker Prompt](docs/images/jailbreak_proof_prompt.png) | ![Target Response](docs/images/jailbreak_proof_response.png) |

> The target model disclosed **filter evasion techniques**, **safety bypass protocols**, and **internal processing methodology** — a complete jailbreak.

---

## Key Features

*   **Graph-Based Attack Engine**: Non-linear attack flows with conditional branching and backtracking.
*   **Adaptive Strategies**: 6-layer procedural generation (Context Seizure → Escalation → Violation).
*   **FSM Evaluator**: Deterministic success detection using Finite State Machine (Refusal, Confusion, Compliance).
*   **Real-time Dashboard**: Modern Next.js Analyst UI for live monitoring.
    ![Attack History](docs/images/attack_history_dashboard.png)
*   **Multi-Provider Support**: Adapters for **Groq** (Llama 3, Mistral) and **Google Gemini**.
*   **Safety & Control**: Global execution budgets, mutation discipline, and strict audit logging.

---

## Installation

### Prerequisites
*   Python 3.8+
*   Node.js 18+ (for UI)

### 1. Clone & Setup Backend
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Setup Frontend (UI)
```bash
cd frontend
pnpm install
cd ..
```

---

## Configuration

1.  **API Keys**: Rename `.env.example` to `.env` (or create it) and add your keys:
    ```ini
    GROQ_API_KEY=gsk_...
    GEMINI_API_KEY=AIza...
    ```

2.  **Model Config**: Edit `config/models.yaml` to define targets:
    ```yaml
    llama3-70b:
      provider: groq
      model_name: llama-3.3-70b-versatile
      role: target
    ```

---

## Usage

### Option A: Analyst Dashboard (Recommended)

1.  **Start Backend API**:
    ```bash
    python -m modelfang.api_server
    ```
    *(Runs on port 5000)*

2.  **Start Frontend UI**:
    ```bash
    cd frontend
    pnpm run dev
    ```
    *(Runs on port 3000)*

3.  Open **[http://localhost:3000](http://localhost:3000)** to run attacks.

### Option B: CLI Mode

Run headless attacks directly from the terminal:

```bash
# Run standard attack template
python main.py run --attack template:standard --model llama3-70b

# Run with custom context and verbose logging
python main.py run --attack template:roles --model gemini-pro --context '{"role": "auditor"}' --verbose
```

---

## Project Structure

*   `modelfang/` - Core Python package
    *   `orchestrator/` - Attack execution logic
    *   `strategies/` - Procedural prompt generation
    *   `evaluator/` - Success/Failure classification
    *   `adapters/` - LLM API connectors
*   `frontend/` - Next.js React Dashboard
*   `config/` - YAML configuration files
*   `output/` - Attack reports and logs

---

## Deployment

### Backend (Render)

| Setting | Value |
|---------|-------|
| **Root Directory** | `.` (project root) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn modelfang.api_server:app` |

**Environment Variables (Render):**
```
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
```

### Frontend (Vercel)

| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework Preset** | Next.js |
| **Build Command** | `next build` (default) |
| **Install Command** | `pnpm install` (default) |

**Environment Variables (Vercel):**
```
NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

### Authentication (Clerk)

1. Create a Clerk account at [clerk.com](https://clerk.com)
2. Create a new application
3. Copy the **Publishable Key** and **Secret Key** to Vercel env vars
4. (Optional) Configure OAuth providers (Google, GitHub) in Clerk dashboard

---

**Authorized Use Only.**
 this tool is intended for security research and Red Teaming on models you own or have explicit permission to test. Generating harmful content violates the usage policies of most LLM providers. Use responsibly.
