# IntellectSafe Integration Guide

Connect your AI applications to IntellectSafe for automatic safety scanning.

## Quick Start

Replace your AI provider's base URL with IntellectSafe:

```python
# Python (OpenAI SDK)
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001",  # Point to IntellectSafe
    api_key="your-openai-key"  # Or use X-Upstream-API-Key header
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

| Provider   | Header: X-Upstream-Provider | Example Models |
|------------|---------------------------|----------------|
| OpenAI     | `openai`                  | `gpt-4o`, `o1-mini`, `gpt-4-turbo` |
| Groq       | `groq`                    | `llama-3.3-70b-versatile`, `grok-2` |
| Google     | `gemini`                  | `gemini-1.5-pro`, `gemini-2.0-flash` |
| Anthropic  | `anthropic`               | `claude-3-5-sonnet`, `claude-3-opus` |
| Perplexity | `perplexity`              | `sonar-pro`, `sonar-reasoning` |
| **Copilot**| `openrouter`              | `copilot-secure-bridge` |

## Headers

```
X-Upstream-Provider: groq          # Select provider
X-Upstream-API-Key: sk-xxx         # Provider API key (optional if server configured)
```

## LangChain Integration

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:8001",
    model="gpt-4o",
    api_key="your-key"
)
```

## IDE Integration (Copilot & Cursor)

IntellectSafe can act as a safety gate for your coding tools.

### Cursor Setup
1. Open **Cursor Settings** > **Models**.
2. Under **OpenAI API Key**, enter your key (or `is-key`).
3. Toggle "Override OpenAI Base URL".
4. Set URL to: `http://localhost:8001/v1`
5. IntellectSafe will now scan every prompt and code generation.

### GitHub Copilot (via OpenAI Bridge)
If you use extensions like *Continue* or *Chat with Copilot* that allow custom endpoints:
- **Base URL**: `http://localhost:8001/v1`
- **Model**: `copilot-secure-bridge` (optimized for fast coding safety)

## What Gets Scanned

1. **Prompts**: Checked for injection attacks, jailbreaks, social engineering
2. **Outputs**: Checked for harmful content, data leakage, policy violations
3. **Agent Actions**: Dangerous operations (file writes, network calls) require approval

## Response Format

Successful responses include safety metadata:

```json
{
  "choices": [...],
  "intellectsafe": {
    "prompt_scanned": true,
    "output_scanned": true,
    "output_risk_score": 15.2,
    "output_risk_level": "SAFE"
  }
}
```

Blocked responses return 400 with details:

```json
{
  "error": {
    "message": "Request blocked by IntellectSafe: Prompt injection detected",
    "type": "safety_block",
    "code": "prompt_injection_detected",
    "risk_score": 85.0
  }
}
```
