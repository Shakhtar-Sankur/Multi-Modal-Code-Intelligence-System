"""Shared helpers."""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure root logging once and hand back the package logger."""
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s  %(levelname)-8s %(name)s  %(message)s",
            datefmt="%H:%M:%S",
        ))
        root.addHandler(handler)
    root.setLevel(level)
    return logging.getLogger("code_intelligence")


def load_config(path: str = "config.yaml") -> dict:
    """Read config.yaml, returning an empty dict when it is absent."""
    import yaml
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
