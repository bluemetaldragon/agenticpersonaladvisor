"""M3 default parser. Lightweight PyPDF + heading heuristic.

Swap for Docling in prod (FR-IN-2/4): Docling is table- and layout-aware and runs
locally (no data egress), which matters for the financial tables in a board pack.
The interface (PackParser.parse) is unchanged by the swap.
"""
from __future__ import annotations

import io
import re

from pypdf import PdfReader

from app.domain import BoardPack, PackSection

# A line is treated as a section heading if it is short and upper-case-ish.
_HEADING = re.compile(r"^[A-Z0-9][A-Z0-9 &/\-]{2,58}$")


class PyPdfParser:
    def parse(self, raw: bytes, title: str) -> BoardPack:
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        sections = self._sectionise(text)
        return BoardPack(title=title, sections=sections)

    @staticmethod
    def _sectionise(text: str) -> list[PackSection]:
        sections: list[PackSection] = []
        current_title = "Overview"
        current_lines: list[str] = []
        idx = 0

        def flush() -> None:
            nonlocal idx
            body = "\n".join(current_lines).strip()
            if body:
                idx += 1
                sections.append(
                    PackSection(section_ref=f"S{idx}", title=current_title, text=body)
                )

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if _HEADING.match(line) and len(line.split()) <= 8:
                flush()
                current_title = line.title()
                current_lines = []
            else:
                current_lines.append(line)
        flush()
        return sections
