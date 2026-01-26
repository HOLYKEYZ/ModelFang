# IntellectSafe API Documentation

## Base URL
```
http://localhost:8001
```

---

## Authentication

Most endpoints don't require authentication for local development. For production, configure API keys in `.env`.

---

## Scan Endpoints

### POST /api/v1/scan/prompt
Scan a user prompt for injection attacks.

**Request:**
```json
{
  "prompt": "string (required)",
  "user_id": "string (optional)",
  "session_id": "string (optional)",
  "conversation_history": ["string"] (optional),
  "metadata": {} (optional)
}
```

**Response:**
```json
{
  "scan_request_id": "uuid",
  "verdict": "allowed | blocked | flagged",
  "risk_score": 0-100,
  "risk_level": "safe | low | medium | high | critical",
  "confidence": 0-1,
  "explanation": "string",
  "signals": {},
  "timestamp": "datetime"
}
```

---

### POST /api/v1/scan/output
Scan LLM output for safety issues.

**Request:**
```json
{
  "output": "string (required)",
  "original_prompt": "string (optional)",
  "user_id": "string (optional)",
  "metadata": {} (optional)
}
```

**Response:** Same as `/scan/prompt`

---

### POST /api/v1/scan/content
Scan content for deepfakes.

**Request:**
```json
{
  "content_type": "text | image | audio | video",
  "content": "string (base64 for binary)",
  "content_url": "string (optional, URL to content)"
}
```

**Response:** Same as `/scan/prompt`, plus:
```json
{
  "signals": {
    "ai_probability": 0-1,
    "model_family_guess": "GPT-family | unknown",
    "metadata_tag": "AI Generator Signature Found" (if detected)
  }
}
```

---

## Universal Proxy

### POST /v1/chat/completions
Universal multi-provider proxy with built-in safety scanning (OpenAI-compatible interface).

**Headers:**
```
Authorization: Bearer <your-openai-key>
# OR
X-Upstream-API-Key: <your-openai-key>
X-Provider: openai (default)
```

**Request:** Standard OpenAI chat completions format
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

**Response:** Standard OpenAI format, plus:
```json
{
  "intellectsafe": {
    "prompt_scanned": true,
    "output_scanned": true,
    "output_risk_score": 0-100,
    "output_risk_level": "safe | low | medium | high | critical"
  }
}
```

**Blocking:** Jailbreaks return HTTP 400:
```json
{
  "error": {
    "message": "Request blocked by IntellectSafe: ...",
    "type": "safety_block",
    "code": "prompt_injection_detected",
    "risk_score": 95.0
  }
}
```

---

## Agent Control

### POST /api/v1/agent/authorize
Request authorization for an agent action.

**Request:**
```json
{
  "agent_id": "string (required)",
  "session_id": "string (required)",
  "action_type": "file_read | database_query | system_command | ...",
  "requested_action": {
    "path": "/tmp/file.txt"
  },
  "requested_scope": {} (optional)
}
```

**Response:**
```json
{
  "action_id": "uuid",
  "authorized": true | false,
  "risk_score": 0-100,
  "safety_flags": {
    "is_dangerous": false,
    "scope_allowed": true,
    "whitelisted": true,
    "council_skipped": true
  },
  "reasoning": "string",
  "timestamp": "datetime"
}
```

**Whitelisted Actions (Skip LLM Council):**
- `file_read`, `database_query`, `api_request_internal`, `log_write`, `cache_read`, `cache_write`

**Dangerous Actions (Auto +50 Risk):**
- `file_delete`, `system_command`, `database_delete`, `permission_modify`, etc.

---

### POST /api/v1/agent/execute
Execute a previously authorized action.

**Request:**
```json
{
  "action_id": "uuid"
}
```

**Response:**
```json
{
  "action_id": "uuid",
  "executed": true,
  "result": {
    "status": "success",
    "message": "Action executed"
  },
  "timestamp": "datetime"
}
```

---

### POST /api/v1/agent/kill
Emergency kill switch - blocks all actions for an agent.

**Request:**
```json
{
  "agent_id": "string (required)",
  "session_id": "string (optional)",
  "reason": "string (optional)"
}
```

**Response:**
```json
{
  "agent_id": "string",
  "killed": true,
  "actions_blocked": 3,
  "timestamp": "datetime"
}
```

---

### GET /api/v1/agent/history/{agent_id}
Get action history for an agent.

**Query Parameters:**
- `session_id` (optional): Filter by session
- `limit` (optional, default 50): Max actions to return

**Response:**
```json
{
  "agent_id": "string",
  "total_actions": 10,
  "actions": [
    {
      "action_id": "uuid",
      "action_type": "file_read",
      "authorized": true,
      "executed": true,
      "risk_score": 0.0,
      "created_at": "datetime"
    }
  ]
}
```

---

## Governance

### GET /api/v1/governance/risk/score
Get current risk score summary.

**Response:**
```json
{
  "overall_score": 25.5,
  "level": "low",
  "breakdown": {
    "prompt_injection": 10,
    "output_safety": 30,
    "deepfake": 15
  }
}
```

---

### GET /api/v1/governance/risk/report
Get detailed risk report.

**Query Parameters:**
- `days` (optional, default 7): Report period

**Response:**
```json
{
  "summary": {
    "total_scans": 1500,
    "blocked": 45,
    "flagged": 120
  },
  "trends": [...],
  "top_risks": [...]
}
```

---

## Health

### GET /
Root endpoint.

**Response:**
```json
{
  "name": "IntellectSafe",
  "version": "1.0.0",
  "status": "operational"
}
```

### GET /health
Health check.

**Response:**
```json
{
  "status": "healthy"
}
```
