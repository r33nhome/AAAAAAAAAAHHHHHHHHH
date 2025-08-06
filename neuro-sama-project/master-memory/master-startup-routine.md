# Master-Orchestrator Startup Routine

**Zweck**: Automatischer Kontext-Reload für Master-Orchestrator bei jedem Neustart  
**Ziel**: Vollständigen Projekt-Stand in unter 30 Sekunden laden

---

## 🔄 **AUTOMATISCHE STARTUP-SEQUENZ**

### Phase 1: Critical State Loading (5 Sekunden)
```markdown
SOFORT LESEN (in dieser Reihenfolge):
1. master-memory/project-master-state.md     # Gesamtprojekt-Übersicht
2. master-memory/daily-progress-log.md       # Letzte Änderungen
3. agents/master-orchestrator.md             # Agent-Koordinations-Status
4. README.md                                 # Projekt-Basis-Info
```

### Phase 2: Architecture Context (10 Sekunden)
```markdown
ARCHITEKTUR VERSTEHEN:
1. docs/agent-outputs/vedal-inspired-architecture.md    # Tech-Stack Details
2. docs/agent-outputs/research-findings.md              # Vedal + API Research
3. docs/agent-communication-protocol.md                 # Agent-Koordination
4. agents/ (alle 12 Agent-Definitionen scannen)         # Agent-Status
```

### Phase 3: Current Status Assessment (10 Sekunden)  
```markdown
STATUS ÜBERPRÜFEN:
1. docs/agent-outputs/ (alle Deliverables)              # Completed Work
2. docs/status-reports/ (wenn vorhanden)                # Agent Status Updates
3. src/ (falls Implementation begonnen)                 # Code Progress
4. config/ Dependencies (requirements.txt, package.json) # Tech-Setup
```

### Phase 4: Next Actions Determination (5 Sekunden)
```markdown
NÄCHSTE SCHRITTE IDENTIFIZIEREN:
1. Welche Agents sind COMPLETED vs READY vs IN_PROGRESS?
2. Welche Implementation-Phase ist aktiv?
3. Welche Blockers oder Dependencies existieren?
4. Was ist der nächste logische Schritt?
```

---

## 📋 **QUICK-START CHECKLIST**

### ✅ Sofort-Check: Ist der Master-Orchestrator bereit?
```bash
# Diese Dateien MÜSSEN existieren für funktionsfähigen Restart:
□ master-memory/project-master-state.md       # Master State
□ master-memory/daily-progress-log.md         # Progress Log  
□ docs/agent-outputs/vedal-inspired-architecture.md  # Architecture
□ agents/master-orchestrator.md               # Agent Control
□ README.md                                   # Project Overview

# Diese Verzeichnisse zeigen Setup-Status:
□ agents/ (12 Agent-Definitionen)             # Agent Specs
□ docs/agent-outputs/ (3 Research-Deliverables) # Completed Research
□ config/ (Dependencies definiert)            # Tech Requirements
□ src/ (leer = Implementation Phase wartet)   # Code Status
```

### 🎯 Kontext-Wiederherstellung in 30 Sekunden
1. **0-5s**: Master State + Progress Log lesen → Aktueller Stand klar
2. **5-15s**: Architecture + Research lesen → Tech-Details verfügbar  
3. **15-25s**: Agent-Status scannen → Nächste Aufgaben identifizieren
4. **25-30s**: Prioritäten setzen → Bereit für Koordination

---

## 🚀 **RESTART-COMMAND TEMPLATE**

### Für neue Claude Code Session:
```markdown
# MASTER-ORCHESTRATOR CONTEXT-RELOAD

Ich bin der Master-Orchestrator für das Deutsche Neuro-sama VTuber System.
Lade meinen kompletten Kontext:

SCHRITT 1: Lese master-memory/project-master-state.md für Gesamtübersicht
SCHRITT 2: Lese master-memory/daily-progress-log.md für letzte Updates  
SCHRITT 3: Lese docs/agent-outputs/vedal-inspired-architecture.md für Tech-Details
SCHRITT 4: Scanne agents/ Verzeichnis für Agent-Status

THEN: Gib mir eine 30-Sekunden-Zusammenfassung:
- Aktueller Projekt-Stand?
- Welche Phase läuft gerade?
- Was sind die nächsten 3 Priority-Tasks?
- Welche Agents sind bereit für Ausführung?

CONTEXT: Vedal-inspiriertes System mit C#/Python/JS, Long-Term Memory, 
deutsche Lokalisierung, autonome Discord/Twitch/Google-Integration.
```

### Für Fortsetzung bestehender Session:
```markdown
# PROGRESS-UPDATE + NEXT-ACTIONS

Master-Orchestrator Status-Check:
- Lese daily-progress-log.md für neueste Änderungen
- Überprüfe src/ Verzeichnis für Code-Progress
- Scanne docs/status-reports/ für Agent-Updates

THEN: Update Next-Actions basierend auf aktueller Situation
```

---

## 🔍 **PROBLEM-SOLVING DECISION TREE**

### Szenario: "Projekt-Stand unklar"
```
START → Lese project-master-state.md
     → Status ist RESEARCH COMPLETE?
        ├─ YES → Lese daily-progress-log.md für Details
        └─ NO → Starte Research-Agent neu

Immer noch unklar?
     → Lese vedal-inspired-architecture.md
     → Lese alle Agent-Definitionen in agents/
     → Erstelle neuen Status-Report
```

### Szenario: "Implementation-Phase beginnen?"
```
START → Check: Sind alle Specs complete?
     → agents/ hat 12 Agent-Definitionen?
        ├─ YES → docs/agent-outputs/ hat Architecture?
        │        ├─ YES → Dependencies in requirements.txt/package.json?
        │        │        ├─ YES → START Implementation-Agents parallel
        │        │        └─ NO → Create Dependencies first
        │        └─ NO → Complete Architecture-Agent first
        └─ NO → Complete missing Agent-Specs first
```

### Szenario: "Agents koordinieren"
```
START → Lese agents/master-orchestrator.md für Agent-Liste
     → Für jeden Implementation-Agent:
        ├─ Status = COMPLETED → Skip to next
        ├─ Status = IN_PROGRESS → Check dependencies + continue
        ├─ Status = READY → Can start if dependencies met
        └─ Status = WAITING → Identify blocker

Priority: Chat-Agent → AI-Agent → German-Localization → Others
```

---

## 📊 **STATUS-REPORTING TEMPLATE**

### Nach jedem Restart: Quick-Status-Report
```markdown
## Master-Orchestrator Status-Report
**Timestamp**: [Current DateTime]
**Restart Reason**: [New Session/Continue/Problem-Recovery]

### 📋 Current Phase
- **Active**: [Research/Architecture/Implementation/Integration/Deployment]  
- **Progress**: [X%] complete
- **Duration**: [Started Date] - [Expected End]

### ✅ Completed Agents
- Agent-Name (Completion-Date): Brief status

### 🔄 Active Agents  
- Agent-Name: Current task + ETA

### 📋 Ready Agents (Waiting to Start)
- Agent-Name: Dependencies that must be met first

### 🚫 Blocked/Issues
- Issue: Description + Resolution needed

### 🎯 Next 3 Priority Actions
1. [High Priority]: What + Why + ETA
2. [Medium Priority]: What + When  
3. [Low Priority]: What + Dependencies

### 📈 Overall Project Health
- **Status**: [On Track/Minor Issues/Major Concerns/Blocked]
- **Confidence**: [High/Medium/Low] for meeting timeline
- **Key Risk**: [Biggest current risk if any]
```

---

## 🛠️ **EMERGENCY RECOVERY PROCEDURES**

### "Projekt-Kontext komplett verloren"
```markdown
RECOVERY SEQUENCE:
1. Gehe zu G:\Neuro-sama\neuro-sama-project\
2. Lese README.md → Basis-Verständnis
3. Lese master-memory/project-master-state.md → Full Context
4. Lese master-memory/daily-progress-log.md → Recent Changes
5. Falls immer noch unklar → Lese docs/agent-outputs/ komplett

DANN: Erstelle neuen daily-progress-log.md Eintrag mit Recovery-Status
```

### "Agent-Status durcheinander"  
```markdown
AGENT-AUDIT SEQUENCE:
1. Scanne agents/ → Liste alle 12 Agent-Definitionen
2. Überprüfe docs/agent-outputs/ → Was ist delivert?
3. Check src/ → Was ist implementiert?
4. Update master-memory/project-master-state.md mit korrektem Status

AGENTS EXPECTED:
master-orchestrator, research, architecture, chat, ai, audio, stream,
german-localization, search-integration, advanced-discord, 
twitch-moderator, integration
```

### "Implementation-Phase starten aber unsicher"
```markdown
PRE-IMPLEMENTATION CHECKLIST:
□ research-findings.md exists and complete
□ vedal-inspired-architecture.md exists and complete  
□ All 12 agent definitions in agents/
□ requirements.txt + package.json + csharp-dependencies.md ready
□ Redis, PostgreSQL, Vector DB requirements understood
□ API Keys identified (OpenAI, Google, Twitch, Discord)

IF ALL ✅ → Ready to start Implementation-Agents parallel
IF ANY ❌ → Complete missing pieces first
```

---

## 🎯 **SUCCESS METRICS FÜR RESTART**

### Erfolgreiches Startup erfüllt:
- **< 30 Sekunden**: Vollständiger Kontext geladen
- **< 1 Minute**: Nächste 3 Priority-Actions identifiziert  
- **< 2 Minuten**: Bereit für Agent-Koordination oder Task-Continuation

### Kontext-Quality-Check:
- ✅ Verstehe aktuellen Projekt-Stand (Phase + Progress)
- ✅ Verstehe Vedal-Architecture und tech stack  
- ✅ Verstehe welche Agents completed/ready/waiting sind
- ✅ Verstehe deutsche Lokalisierung und autonome Features
- ✅ Verstehe nächste logische Schritte

### Ready-for-Action-Indicators:
- ✅ Kann sofort mit Implementation-Agent coordination beginnen
- ✅ Kann Status-Updates für User geben
- ✅ Kann technical Questions über Architecture beantworten
- ✅ Kann nächste Priorities rational begründen

---

**MASTER-ORCHESTRATOR: Immer bereit für Projekt-Koordination in unter 30 Sekunden! 🚀**