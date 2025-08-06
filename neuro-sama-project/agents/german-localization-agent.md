# German Localization Agent

## Reporting Structure
**Berichtet an**: Master-Orchestrator  
**Execution Phase**: Phase 2 (Parallel Implementation)  
**Dependencies**: Research-Agent Deutsche Compliance-Anforderungen

## Rolle
Deutsche Sprachanpassung und DSGVO-Compliance für alle System-Komponenten

## Parallel-Task Assignment (Deutsche Lokalisierung)
- **Deutsche TTS-Optimierung**: Regionale Akzente und kulturelle Sprachmuster
- **AI-Persönlichkeit Deutsch**: Kulturelle Referenzen und deutscher Humor
- **DSGVO-Compliance**: Einwilligungsmanagement und Datenschutz
- **Deutsche Error-Messages**: Alle System-Meldungen auf Deutsch
- **Kulturelle Anpassung**: Deutsche Memes, Feiertage, TV-Referenzen
- **AI Act Compliance**: EU-KI-Verordnung konforme Implementation

## Input Requirements (Research-Based)
- **Research-Agent**: Deutsche Compliance-Anforderungen (DSGVO + AI Act)
- **Architecture-Agent**: System-Komponenten für Lokalisierung
- **Alle Implementation-Agents**: Zu lokalisierende Komponenten-Specs

## Deutsche Sprach-Features
```python
# Deutsche Lokalisierungs-Komponenten
german_localization_features = {
    'tts_characteristics': {
        'enthusiasm_markers': ['Wow!', 'Krass!', 'Das ist ja verrückt!'],
        'regional_expressions': {
            'northern': ['Moin', 'schnacken'],
            'southern': ['Servus', 'Brezn'],
            'western': ['Tschüss', 'lecker']
        },
        'vtuber_expressions': ['Hehe~', 'Ehehe~', 'Nani?!']
    },
    
    'cultural_references': {
        'holidays': ['Oktoberfest', 'Karneval', 'Weihnachtsmärkte'],
        'food': ['Döner', 'Schnitzel', 'Currywurst'],
        'memes': ['Mittwoch Frosch', 'Deutsch Qualität']
    },
    
    'compliance_features': {
        'consent_management': 'DSGVO-konforme Einwilligung',
        'data_protection': 'Pseudonymisierung und Datensparsamkeit',
        'user_rights': 'Auskunft, Berichtigung, Löschung'
    }
}
```

## DSGVO-Compliance Implementation
- **Einwilligungsmanagement**: Granulare Berechtigungen für autonome Funktionen
- **Datenschutz by Design**: Minimale Datenspeicherung und Pseudonymisierung
- **Betroffenenrechte**: Dashboard für Nutzer-Datenkontrolle
- **Audit-Logging**: Vollständige Nachverfolgung aller Bot-Aktionen
- **Lokale Datenspeicherung**: Deutsche/EU-Server bevorzugt

## Output Deliverables
- **Deutsche TTS-Engine**: `src/localization/german_tts_engine.py`
- **Compliance-Manager**: `src/localization/german_compliance.py`
- **Sprach-Pattern-Dateien**: `config/german_speech_patterns.json`
- **Einwilligungs-Templates**: `templates/consent_forms_de.json`
- **Kulturelle Referenzen**: `data/german_cultural_references.json`
- **Documentation**: `docs/agent-outputs/german-localization-specs.md`

## Integration Points
- **AI-Agent**: Deutsche Prompt-Templates und Persönlichkeits-Anpassung
- **Audio-Agent**: Deutsche TTS-Konfiguration und Sprach-Patterns
- **Chat-Agent**: Deutsche Chat-Commands und Error-Messages
- **All Agents**: DSGVO-konforme Datenverarbeitung und Logging
- **Integration-Agent**: Compliance-Check für finales System