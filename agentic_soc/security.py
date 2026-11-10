"""Input boundaries, output minimisation and research scope checks."""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import re
from datetime import datetime, timezone
from pathlib import Path


class BoundaryError(ValueError):
    """Rejected input; error messages deliberately contain no evidence values."""


def contained(path: str | Path, roots: list[Path], *, file: bool = True) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute():
        raise BoundaryError("Use an absolute path; relative evidence paths are not accepted.")
    p = p.resolve(strict=True)
    if not any(p.is_relative_to(r.resolve()) for r in roots):
        raise BoundaryError("Path is outside the operator-configured allowed roots.")
    if file and (not p.is_file() or p.stat().st_size > 50 * 1024 * 1024):
        raise BoundaryError("Evidence must be a regular file no larger than 50 MiB.")
    if any(x.lower() in {".ssh", ".aws", ".config", ".git"} for x in p.parts):
        raise BoundaryError("Credential/configuration stores cannot be imported.")
    if p.name.lower() in {".env", "auth.json", "credentials", "config.yaml"}:
        raise BoundaryError("Credential/configuration files cannot be imported.")
    return p


class Redactor:
    """Best-effort minimisation, not a guarantee of anonymisation or GDPR compliance."""

    def __init__(self, salt: bytes):
        self.salt = salt

    def token(self, value: str, kind: str = "entity") -> str:
        digest = hmac.new(self.salt, value.encode(), hashlib.sha256).hexdigest()[:12]
        return f"[{kind}-{digest}]"

    def text(self, value: object) -> str:
        text = str(value)
        text = re.sub(r"(?i)\b(?:password|passwd|token|secret|authorization|ntlm|lmhash)\s*[:=]\s*\S+",
                      "[credential-redacted]", text)
        # Opaque hash strings in prose may be credentials. Keep malware hashes only
        # in explicitly typed artifact fields, never free text.
        text = re.sub(r"\b[0-9a-fA-F]{32,128}\b", "[hash-in-text-redacted]", text)
        text = re.sub(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", lambda m: self.token(m[0], "email"), text)
        text = re.sub(r"(?i)([A-Z]:\\Users\\|/home/|/Users/)([^/\\\s]+)",
                      lambda m: m[1] + self.token(m[2], "user"), text)
        text = re.sub(r"\bS-1-\d+(?:-\d+){1,15}\b", lambda m: self.token(m[0], "sid"), text)
        def ip(match):
            try:
                ipaddress.ip_address(match[0])
                return self.token(match[0], "ip")
            except ValueError:
                return match[0]
        text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", ip, text)
        # Explicit IPv6 literals, including compressed forms.
        text = re.sub(r"(?<!\w)(?:[0-9a-fA-F]{0,4}:){2,}[0-9a-fA-F:.]*(?!\w)", ip, text)
        return text[:4000]

    def clean(self, value):
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                low = str(key).lower()
                if any(x in low for x in ("password", "secret", "ntlm", "firstbytes", "matched", "token")):
                    result[key] = "[redacted]"
                elif low in {"md5", "sha1", "sha256"} and isinstance(item, str) and re.fullmatch(r"[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", item):
                    result[key] = item.lower()
                else:
                    result[key] = self.clean(item)
            return result
        if isinstance(value, list):
            return [self.clean(x) for x in value]
        return self.text(value) if isinstance(value, str) else value


def check_scope(scope: dict, target: str, now: datetime | None = None) -> dict:
    """Check declared scope, not legal validity of the author's authorization."""
    if not isinstance(scope, dict):
        raise BoundaryError("A structured research scope is required.")
    needed = {"targets", "authorization_ref", "valid_from", "valid_until", "rules_of_engagement", "allowed_activities"}
    if not needed <= scope.keys():
        raise BoundaryError("Scope is incomplete.")
    if not isinstance(scope["targets"], list) or target not in scope["targets"]:
        raise BoundaryError("Target must exactly match a declared scope target; no wildcards.")
    if not isinstance(scope["authorization_ref"], str) or len(scope["authorization_ref"].strip()) < 8:
        raise BoundaryError("An operator-reviewable authorization reference is required.")
    roe = scope["rules_of_engagement"]
    if not isinstance(roe, str) or len(roe.strip()) < 20:
        raise BoundaryError("Rules of engagement must be explicit.")
    activities = scope["allowed_activities"]
    allowed = {"research", "emulation-planning", "detection-engineering", "lab-validation"}
    if not isinstance(activities, list) or not activities or not set(activities) <= allowed:
        raise BoundaryError("Only research, planning, detection engineering and lab validation are supported.")
    try:
        start, end = (datetime.fromisoformat(scope[k].replace("Z", "+00:00")) for k in ("valid_from", "valid_until"))
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise BoundaryError("Scope timestamps must be timezone-aware ISO 8601.") from None
    now = now or datetime.now(timezone.utc)
    if not start <= now <= end:
        raise BoundaryError("Scope is expired or not yet valid.")
    return {"valid": True, "authorization_verified": False, "activities": activities,
            "limitation": "Declared scope checked; operator must verify legal authorization. Planning only, no target interaction."}


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
