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
            "results",
            "limits",
            "reproduction",
        ),
    )
    _require_string(artifact["question"], "question")
    if "title" in artifact:
        _require_string(artifact["title"], "title")

    # Preserve the original renderer contract for existing artifacts. New
    # artifacts should set analysis_type and receive the stronger mode-specific
    # evidence checks documented by this skill.
    if "analysis_type" not in artifact:
        data = _require_mapping(artifact["data"], "data")
        _require_fields(data, "data", ("grain", "n"))
        _require_string(data["grain"], "data.grain")
        _require_positive_integer(data["n"], "data.n")
        methods = _require_mapping(artifact["methods"], "methods")
        _require_fields(methods, "methods", ("baseline",))
        _require_string(methods["baseline"], "methods.baseline")
        validation = _require_mapping(artifact.get("validation"), "validation")
        _require_fields(validation, "validation", ("design", "primary_metric"))
        for field in ("design", "primary_metric"):
            _require_string(validation[field], f"validation.{field}")
        _require_mapping(artifact["results"], "results")
        limits = artifact["limits"]
        if not isinstance(limits, list) or not limits:
            raise ValueError("limits must be a non-empty array of strings")
        for index, item in enumerate(limits):
            _require_string(item, f"limits[{index}]")
        _require_mapping(artifact["reproduction"], "reproduction")
        if "interpretation" in artifact:
            _require_string(artifact["interpretation"], "interpretation")
        artifact["analysis_type"] = (
            "simulation" if "simulation" in methods else "predictive"
        )
        return artifact

    analysis_type = _require_string(
        artifact["analysis_type"], "analysis_type"
    ).lower()
    allowed = {
        "descriptive", "explanatory", "predictive",
        "causal", "ranking", "simulation",
    }
    if analysis_type not in allowed:
        raise ValueError(
            "analysis_type must be descriptive, explanatory, predictive, "
            "causal, ranking, or simulation"
        )
    artifact["analysis_type"] = analysis_type
    data = _require_mapping(artifact["data"], "data")
    _require_fields(data, "data", ("source", "sport", "grain", "period", "n"))
    for field in ("source", "sport", "grain", "period"):
        _require_string(data[field], f"data.{field}")
    _require_positive_integer(data["n"], "data.n")

    methods = _require_mapping(artifact["methods"], "methods")
    mode_fields = {
        "descriptive": ("summary",),
        "explanatory": ("estimand", "design"),
        "predictive": ("target", "decision_time", "baseline", "candidate"),
        "causal": ("treatment", "outcome", "identification"),
        "ranking": ("as_of", "baseline", "candidate"),
        "simulation": ("simulation", "assumptions"),
    }
    _require_fields(methods, "methods", mode_fields[analysis_type])
    for field in mode_fields[analysis_type]:
        value = methods[field]
        if field == "assumptions":
            if not isinstance(value, list) or not value:
                raise ValueError("methods.assumptions must be a non-empty array")
            for index, item in enumerate(value):
                _require_string(item, f"methods.assumptions[{index}]")
        else:
            _require_string(value, f"methods.{field}")

    validation = artifact.get("validation")
    if analysis_type in {"predictive", "ranking"}:
        validation = _require_mapping(validation, "validation")
        _require_fields(
            validation,
            "validation",
            ("design", "primary_metric", "metric_direction", "comparison_population"),
        )
        for field in ("design", "primary_metric", "comparison_population"):
            _require_string(validation[field], f"validation.{field}")
        direction = _require_string(
            validation["metric_direction"], "validation.metric_direction"
        ).lower()
        if direction not in {"lower", "higher"}:
            raise ValueError("validation.metric_direction must be lower or higher")
    elif validation is not None:
        _require_mapping(validation, "validation")

    _require_mapping(artifact["results"], "results")

    if "interpretation" in artifact:
        _require_string(artifact["interpretation"], "interpretation")
    limits = artifact["limits"]
    if not isinstance(limits, list) or not limits:
        raise ValueError("limits must be a non-empty array of strings")
    for index, item in enumerate(limits):
        _require_string(item, f"limits[{index}]")

    reproduction = _require_mapping(artifact["reproduction"], "reproduction")
    if not any(key in reproduction for key in ("artifact", "artifacts")):
        raise ValueError("reproduction must identify artifact or artifacts")
    return artifact


def _json_block(value: Any) -> list[str]:
    return ["```json", json.dumps(value, indent=2, sort_keys=True), "```", ""]


def render(doc: dict[str, Any]) -> str:
    title = str(doc.get("title") or "Sports analysis results")
    lines = [
        f"# {title}", "", f"Analysis type: {doc['analysis_type']}", "",
        "## Question", doc["question"].strip(), "",
    ]

    for heading, field in (
        ("Data", "data"),
        ("Methods", "methods"),
        ("Results", "results"),
    ):
        lines.extend([f"## {heading}", ""])
        lines.extend(_json_block(doc[field]))

    if "validation" in doc:
        lines.extend(["## Validation", ""])
        lines.extend(_json_block(doc["validation"]))

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
