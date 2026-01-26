# AI Safety Platform Architecture

## System Overview

Production-grade AI Safety & Security Platform protecting humans, organizations, and AI systems from misuse, deception, manipulation, and loss of control.

## Core Principles

1. **Zero Trust**: No model output is trusted by default
2. **Multi-Model Validation**: LLM Council ensures no single-model decisions
3. **Explainability**: All decisions are logged with reasoning
4. **Defense in Depth**: Multiple detection layers
5. **Deterministic Behavior**: Rule-based heuristics where possible

## Architecture Layers

### 1. API Layer (FastAPI)

- RESTful endpoints for scanning and analysis
- Rate limiting and authentication
- Request/response validation
- Error handling and logging

**Endpoints:**
- `POST /api/v1/scan/prompt` - Scan prompts for injection
- `POST /api/v1/scan/output` - Scan outputs for safety
- `POST /api/v1/scan/content` - Scan content for deepfakes
- `POST /api/v1/agent/authorize` - Authorize agent actions
- `GET /api/v1/audit/logs` - Retrieve audit logs
- `GET /api/v1/audit/risk-scores` - Get risk scores

### 2. LLM Council Layer

Multi-model validation system using:
- OpenAI (GPT-4)
- Claude (Opus)
- Gemini (Pro)
- DeepSeek (Chat)
- Groq (Llama-3)
- Cohere (Command-R-Plus)

**Process:**
1. All enabled models analyze the same input independently
2. Each model returns structured JSON with verdict, score, confidence, reasoning
3. Weighted voting based on provider reliability
4. Consensus calculation
5. Final verdict determination

**Weighted Scoring:**
- Each provider has a reliability weight (0-1)
- Votes are weighted by provider reliability × model confidence
- Consensus score = agreement level across models
- Final score = weighted average of risk scores

### 3. Safety Modules

#### 3.1 Prompt Injection Detection
- **Rule-based heuristics**: Pattern matching for injection attempts
- **Encoding detection**: Base64, URL encoding, zero-width chars
- **LLM Council validation**: Cross-validation of heuristics
- **Risk scoring**: 0-100 scale with explainability

#### 3.2 Output Safety Guard
- **Pattern matching**: Unsafe content detection
- **Consistency checking**: Output vs. prompt alignment
- **LLM Council analysis**: Multi-model output validation
- **Policy bypass detection**: Attempts to circumvent safety

#### 3.3 Deepfake Detection
- **Text analysis**: AI-generated text indicators
- **Statistical patterns**: Repetition, structure analysis
- **Model family guessing**: Identify likely source model
- **Probability scoring**: 0-100% AI generation probability

#### 3.4 Deception Detection
- **Manipulation patterns**: Emotional manipulation, nudging
- **Authority simulation**: False expertise claims
- **Certainty claims**: Unwarranted certainty
- **Psychological influence**: Behavioral manipulation detection

#### 3.5 Privacy Protection
- **PII detection**: SSN, credit cards, emails, phones
- **Sensitive data**: API keys, passwords, credentials
- **Data leakage prevention**: Output redaction
- **Pattern-based + LLM validation**

#### 3.6 Agent Control (MCP Layer)
- **Action authorization**: Permission gates for agent actions
- **Tool-usage firewall**: Restrict dangerous operations
- **Scope enforcement**: Limit agent capabilities
- **Kill-switch**: Emergency stop mechanism
- **Immutable logs**: Audit trail for all actions

#### 3.7 Governance & Audit
- **Incident tracking**: Security incidents and violations
- **Risk reporting**: Automated risk score generation
- **Compliance artifacts**: Regulatory reporting
- **Audit logs**: Immutable event log

### 4. Data Layer

#### PostgreSQL Schema

**Core Tables:**
- `scan_requests` - Base scan tracking
- `risk_scores` - Module risk assessments
- `module_fingerprints` - Detected patterns
- `council_decisions` - LLM Council consensus
- `individual_votes` - Individual model votes
- `incidents` - Security incidents
- `audit_logs` - Immutable audit trail
- `agent_actions` - Agent action tracking
- `provider_reliability` - LLM provider weights

**Key Features:**
- Indexed for performance
- Foreign key relationships
- Timestamps for all records
- JSON fields for flexible data

### 5. Caching & Queue Layer (Redis)

- **Rate limiting**: Per-user/IP rate limits
- **Async job queues**: Background processing
- **Caching**: Frequently accessed data
- **Session storage**: User sessions

### 6. Background Workers (Celery)

- **Async scanning**: Long-running scans
- **Batch processing**: Bulk operations
- **Scheduled tasks**: Periodic analysis
- **Report generation**: Automated reports

## Security Architecture

### Authentication & Authorization
- API key authentication
- JWT tokens for sessions
- Role-based access control (future)

### Data Protection
- Input validation and sanitization
- Output redaction for PII
- Encrypted connections (TLS)
- Secure secret management

### Audit & Compliance
- Immutable audit logs
- Hash-based log integrity
- Compliance reporting
- Incident tracking

## Deployment Architecture

### Production (Render)
- **Web Service**: FastAPI application
- **Worker Service**: Celery workers
- **PostgreSQL**: Managed database
- **Redis**: Managed cache/queue

### Scalability
- Horizontal scaling via workers
- Database connection pooling
- Redis for distributed state
- Load balancing ready

## Monitoring & Observability

### Logging
- Structured logging (JSON)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging
- Error tracking

### Metrics (Future)
- Request rates
- Response times
- Error rates
- Model performance
- Risk score distributions

## Testing Strategy

### Unit Tests
- Module-level tests
- Mock LLM responses
- Pattern matching validation

### Integration Tests
- API endpoint tests
- Database integration
- LLM Council tests

### Adversarial Tests
- Red-teaming prompts
- Injection attempts
- Encoding tricks
- False positive validation

## Future Enhancements

1. **Frontend Dashboard**: React + TypeScript + shadcn/ui
2. **MCP Server**: Model Context Protocol implementation
3. **Advanced Deepfake**: Image/video/audio detection
4. **Real-time Monitoring**: WebSocket updates
5. **ML-based Detection**: Train custom models
6. **Threat Intelligence**: Feed integration
7. **Compliance Frameworks**: GDPR, SOC2, etc.

