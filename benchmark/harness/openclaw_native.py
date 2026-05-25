"""Minimal openclaw_native shim — only provides load_json_file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(workspace: str | Path, filename: str) -> tuple[dict[str, Any] | None, str]:
    path = Path(workspace) / filename
    if not path.exists():
        return None, f"missing {filename}"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"
    if not isinstance(raw, dict):
        return None, f"{filename} must contain a JSON object"
    return raw, f"loaded {filename}"
