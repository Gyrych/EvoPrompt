from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import logging


def setup_file_logger(log_dir: Path | str = "logs") -> logging.Logger:
    p = Path(log_dir)
    p.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    logfile = p / f"{ts}_run.log"

    logger = logging.getLogger(f"evo_prompt_{ts}")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # also attach a simple console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger


def log_response(log_dir: Path | str, filename: str, obj: dict) -> Path:
    p = Path(log_dir)
    p.mkdir(parents=True, exist_ok=True)
    out = p / filename
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return out


