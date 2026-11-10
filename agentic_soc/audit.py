"""Append-only by convention, local, minimised audit metadata."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

_LOCK = threading.Lock()


class Audit:
    def __init__(self, root: Path):
        self.root = root

    def write(self, action: str, status: str, **metadata):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        record = {"time": datetime.now(timezone.utc).isoformat(), "action": action,
                  "status": status, **metadata}
        # Caller passes only numeric counters, generated IDs and exception classes.
        data = (json.dumps(record, ensure_ascii=False) + "\n").encode()
        with _LOCK:
            fd = os.open(self.root / "audit.jsonl", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                os.write(fd, data)
            finally:
                os.close(fd)
