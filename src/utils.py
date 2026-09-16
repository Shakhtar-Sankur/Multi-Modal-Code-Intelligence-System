"""Shared helpers: logging, config and device selection."""
import logging
import sys

import torch


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


def resolve_device(requested=None):
    """Pick a torch device, falling back to CPU when CUDA is not available.

    config.yaml ships `device: cuda`, so on any machine without a GPU the model
    landed on CPU while the inputs were sent to CUDA, and inference died on a
    device mismatch. Asking for cuda without cuda now warns and uses the CPU.
    """
    if requested in (None, 'auto'):
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if str(requested).startswith('cuda') and not torch.cuda.is_available():
        logging.warning("device=%s requested but CUDA is unavailable; using CPU", requested)
        return torch.device('cpu')
    return torch.device(requested)
