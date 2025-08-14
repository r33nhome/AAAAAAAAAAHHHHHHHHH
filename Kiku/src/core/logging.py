# src/core/logging.py
from __future__ import annotations
import logging
import sys
import structlog

def setup_logging(level: int | str = "INFO") -> None:
    """
    Einfaches Logging-Setup mit structlog + Reduktion von voice_recv-Logspam.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    # Standard-Formatter
    fmt = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    # Falls schon Handler bestehen (Neustarts), nicht doppelt anhängen
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        root.addHandler(handler)
    root.setLevel(level)

    # Discord-Logger feinjustieren
    logging.getLogger("discord").setLevel(logging.INFO)
    logging.getLogger("discord.client").setLevel(logging.INFO)
    logging.getLogger("discord.gateway").setLevel(logging.INFO)
    logging.getLogger("discord.voice_state").setLevel(logging.INFO)

    # voice_recv: auf WARNING runterdrehen (SenderReport-Spam ausblenden)
    logging.getLogger("discord.ext.voice_recv").setLevel(logging.WARNING)
    logging.getLogger("discord.ext.voice_recv.reader").setLevel(logging.WARNING)
    logging.getLogger("discord.ext.voice_recv.router").setLevel(logging.WARNING)

    # structlog konfigurieren (human readable)
    try:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.dev.ConsoleRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
    except Exception:
        # Fallback ohne structlog
        pass
