# sehr einfache Blockliste; später ersetzen
BLOCKLIST = {"slur1", "slur2", "badword1", "badword2"}

def is_blocked(text: str) -> bool:
    t = (text or "").lower()
    return any(b in t for b in BLOCKLIST)
