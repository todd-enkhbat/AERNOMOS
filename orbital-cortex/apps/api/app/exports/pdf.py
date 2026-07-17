"""HTML → PDF rendering for mission briefs via Jinja2 + WeasyPrint."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_mission_brief_html(document: Dict[str, Any]) -> str:
    template = _env().get_template("mission_brief.html")
    return template.render(doc=document)


def render_mission_brief_pdf(
    document: Dict[str, Any],
    *,
    html_override: Optional[str] = None,
) -> bytes:
    """Render PDF bytes. Callers may inject html_override for tests."""
    html = html_override if html_override is not None else render_mission_brief_html(document)
    try:
        from weasyprint import HTML
    except ImportError as exc:  # pragma: no cover - exercised when OS libs missing
        raise RuntimeError(
            "WeasyPrint is not available. Install weasyprint and system libraries "
            "(pango, cairo, gdk-pixbuf)."
        ) from exc
    return HTML(string=html, base_url=str(_TEMPLATE_DIR)).write_pdf()
