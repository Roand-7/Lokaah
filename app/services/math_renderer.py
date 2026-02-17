from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MathRenderResult:
    html: str
    latex: str
    engine: str


class MathRenderer:
    """
    Render LaTeX to HTML. Uses latex2mathml when available.
    Falls back to a KaTeX-friendly HTML wrapper for client-side rendering.
    """

    def __init__(self, prefer_mathml: bool = True) -> None:
        self.prefer_mathml = prefer_mathml

    def render(self, latex: str) -> MathRenderResult:
        safe = latex.strip()
        if not safe:
            return MathRenderResult(html="", latex="", engine="none")

        if self.prefer_mathml:
            html = self._try_mathml(safe)
            if html:
                return MathRenderResult(html=html, latex=safe, engine="mathml")

        # KaTeX client-side integration hook.
        html = f"<span class=\"katex\" data-latex=\"{self._escape_attr(safe)}\"></span>"
        return MathRenderResult(html=html, latex=safe, engine="katex-client")

    def _try_mathml(self, latex: str) -> Optional[str]:
        try:
            from latex2mathml.converter import convert  # type: ignore

            mathml = convert(latex)
            return f"<span class=\"mathml\">{mathml}</span>"
        except Exception:
            return None

    def _escape_attr(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("\"", "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
