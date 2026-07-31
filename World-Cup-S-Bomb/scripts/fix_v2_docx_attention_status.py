"""Synchronize the optional-attention paragraph in the canonical Word report."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from docx import Document


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCX_PATH = PROJECT_ROOT / "results/Summary/final_summary.docx"
SUMMARY_PATH = PROJECT_ROOT / "results/reports/model_summary.json"


def main() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    gate = summary.get("metric_gate", {})
    selected_layer = summary.get("selected_layer", "role_aware_fallback")
    enabled = bool(gate.get("enabled", False))
    passed = bool(gate.get("metric_gate_passed", False))
    document = Document(DOCX_PATH)
    matches = [
        paragraph
        for paragraph in document.paragraphs
        if paragraph.text.startswith(
            "The attention layer is disabled by default"
        )
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one attention-status paragraph, found {len(matches)}"
        )
    if enabled:
        status = (
            "passed and was selected"
            if passed
            else "did not pass; the role-aware fallback was retained"
        )
        text = (
            "The optional attention layer was enabled in this canonical run "
            f"and {status}. The selected production layer is "
            f"{selected_layer}."
        )
    else:
        text = (
            "The optional attention layer was disabled in this canonical run, "
            "so no attention metrics are published. The interpretable "
            f"{selected_layer} remains the selected production layer."
        )
    matches[0].text = text
    with tempfile.NamedTemporaryFile(
        suffix=".docx",
        dir=DOCX_PATH.parent,
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
    try:
        document.save(temporary)
        os.replace(temporary, DOCX_PATH)
    finally:
        temporary.unlink(missing_ok=True)
    print(text)


if __name__ == "__main__":
    main()
