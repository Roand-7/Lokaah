from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DiagramResult:
    svg: Optional[str] = None
    ascii: Optional[str] = None


class DiagramGenerator:
    """
    Minimal diagram generator. Returns simple SVG text for embedding.
    Replace with a real diagram engine when available.
    """

    async def generate(self, description: str, style: str, language: str) -> DiagramResult:
        cleaned = description.strip()
        if not cleaned:
            return DiagramResult()

        svg = (
            "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"320\" height=\"180\" viewBox=\"0 0 320 180\">"
            "<rect width=\"100%\" height=\"100%\" fill=\"#ffffff\" stroke=\"#111111\" stroke-width=\"2\"/>"
            "<text x=\"16\" y=\"32\" font-family=\"Arial\" font-size=\"12\" fill=\"#111111\">"
            "Diagram</text>"
            f"<text x=\"16\" y=\"54\" font-family=\"Arial\" font-size=\"12\" fill=\"#333333\">"
            f"{self._escape_svg(cleaned[:120])}</text>"
            "</svg>"
        )

        return DiagramResult(svg=svg)

    def _escape_svg(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&apos;")
        )
