# Agent Communication Protocol

## Communication Structure
Master-Orchestrator koordiniert alle Sub-Agents über shared docs/ Ordner

## Directory Structure
```
docs/
├── agent-inputs/          # Input-Requirements für alle Agents
├── agent-outputs/         # Deliverables von jedem Agent
├── status-reports/        # Real-time Status-Updates
├── coordination/          # Cross-Agent Coordination Messages
└── agent-communication-protocol.md
```

## Communication Flow

### Phase 1: Research Phase
1. **Master-Orchestrator** → `agent-inputs/research-requirements.md`
2. **Research-Agent** → `agent-outputs/research-findings.md`
3. **Research-Agent** → `status-reports/research-status.md`

### Phase 2: Parallel Implementation
1. **Master-Orchestrator** → `agent-inputs/architecture-requirements.md`
2. **Architecture-Agent** → `agent-outputs/system-architecture.md`
3. **Master-Orchestrator** distributes Architecture-Specs to Implementation-Agents
4. **All Implementation-Agents** parallel execution:
   - Chat-Agent → `agent-outputs/chat-integration-specs.md`
   - AI-Agent → `agent-outputs/ai-engine-specs.md`  
   - Audio-Agent → `agent-outputs/audio-system-specs.md`
   - Stream-Agent → `agent-outputs/streaming-integration-specs.md`

### Phase 3: Final Integration
1. **Master-Orchestrator** → `agent-inputs/integration-requirements.md`
2. **Integration-Agent** consumes all `agent-outputs/*`
3. **Integration-Agent** → `agent-outputs/final-system-integration.md`

## Status Reporting Protocol
- **Real-time Updates**: Every Agent schreibt Status-Updates in `status-reports/`
- **Conflict Resolution**: Master-Orchestrator löst Conflicts über `coordination/`
- **Dependency Tracking**: Master überwacht Dependencies und blocked States

## File Naming Convention
- Input-Files: `{agent-name}-requirements.md`
- Output-Files: `{agent-name}-{deliverable-type}.md`
- Status-Files: `{agent-name}-status.md`
- Coordination: `{issue-type}-{timestamp}.md`