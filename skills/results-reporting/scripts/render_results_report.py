#!/usr/bin/env python3
"""Render Markdown from a user-owned sports results JSON artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field} must be a non-empty JSON object")
    return value


def _require_fields(value: dict[str, Any], field: str, required: tuple[str, ...]) -> None:
    missing = [key for key in required if key not in value]
    if missing:
        raise ValueError(f"{field} missing required fields: {', '.join(missing)}")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_positive_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def validate(doc: Any) -> dict[str, Any]:
    artifact = _require_mapping(doc, "root")
    _require_fields(
        artifact,
        "root",
        (
            "question",
            "data",
            "methods",
            "validation",
            "results",
            "limits",
            "reproduction",
        ),
    )
    _require_string(artifact["question"], "question")
    if "title" in artifact:
        _require_string(artifact["title"], "title")

    data = _require_mapping(artifact["data"], "data")
    _require_fields(data, "data", ("grain", "n"))
    _require_string(data["grain"], "data.grain")
    _require_positive_integer(data["n"], "data.n")

    methods = _require_mapping(artifact["methods"], "methods")
    _require_fields(methods, "methods", ("baseline",))
    _require_string(methods["baseline"], "methods.baseline")

    validation = _require_mapping(artifact["validation"], "validation")
    _require_fields(validation, "validation", ("design", "primary_metric"))
    for field in ("design", "primary_metric"):
        _require_string(validation[field], f"validation.{field}")

    _require_mapping(artifact["results"], "results")

    if "interpretation" in artifact:
        _require_string(artifact["interpretation"], "interpretation")
    limits = artifact["limits"]
    if not isinstance(limits, list) or not limits:
        raise ValueError("limits must be a non-empty array of strings")
    for index, item in enumerate(limits):
        _require_string(item, f"limits[{index}]")

    _require_mapping(artifact["reproduction"], "reproduction")
    return artifact


def _json_block(value: Any) -> list[str]:
    return ["```json", json.dumps(value, indent=2, sort_keys=True), "```", ""]


def render(doc: dict[str, Any]) -> str:
    title = str(doc.get("title") or "Sports analysis results")
    lines = [f"# {title}", "", "## Question", doc["question"].strip(), ""]

    for heading, field in (
        ("Data", "data"),
        ("Methods", "methods"),
        ("Validation", "validation"),
        ("Results", "results"),
    ):
        lines.extend([f"## {heading}", ""])
        lines.extend(_json_block(doc[field]))

    interpretation = doc.get("interpretation", "State what changed relative to the named baseline.")
    lines.extend(["## Interpretation", interpretation, "", "## Limits", ""])
    lines.extend([f"- {item}" for item in doc["limits"]])
    lines.extend(["", "## Reproduction", ""])
    lines.extend(_json_block(doc["reproduction"]))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", required=True, help="Input results artifact")
    parser.add_argument("--out", default="data/results_report.md")
    args = parser.parse_args()

    source = Path(args.json)
    if not source.is_file():
        parser.error(f"--json does not exist: {source}")
    if source.suffix.lower() != ".json":
        parser.error("--json must point to a .json file")
    out = Path(args.out)
    if out.suffix.lower() not in {".md", ".markdown"}:
        parser.error("--out must end in .md or .markdown")

    try:
        doc = validate(json.loads(source.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    markdown = render(doc)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    print(markdown, end="")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
