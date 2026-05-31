"""JSON output for realmon."""

from __future__ import annotations

import json

from realmon.models import SystemSnapshot


def render_json(snapshot: SystemSnapshot) -> str:
    """Render system snapshot as JSON string."""
    return json.dumps(snapshot.model_dump(), indent=2, ensure_ascii=False)
