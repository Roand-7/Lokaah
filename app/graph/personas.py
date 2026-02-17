from __future__ import annotations

from typing import Dict


PERSONA_META: Dict[str, Dict[str, str]] = {
    "veda": {
        "label": "VEDA",
        "emoji": "🧠",
        "color": "blue",
    },
    "oracle": {
        "label": "ORACLE",
        "emoji": "🔮",
        "color": "purple",
    },
    "spark": {
        "label": "SPARK",
        "emoji": "⚡",
        "color": "orange",
    },
    "pulse": {
        "label": "PULSE",
        "emoji": "💚",
        "color": "green",
    },
    "atlas": {
        "label": "ATLAS",
        "emoji": "🗓️",
        "color": "teal",
    },
}


def build_prefixed_text(agent_name: str, text: str) -> str:
    """Return clean text without agent prefixes - just the human conversation."""
    return text
