from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
BRIDGE = "sports-ds-bridge"


def _skill_dirs() -> list[Path]:
    return sorted(path for path in SKILLS.iterdir() if (path / "SKILL.md").is_file())


def _frontmatter(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill_file} has no YAML frontmatter"
    end = text.find("\n---\n", 4)
    assert end >= 0, f"{skill_file} has unterminated YAML frontmatter"

    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def test_skill_frontmatter_names_match_directories() -> None:
    for skill_dir in _skill_dirs():
        fields = _frontmatter(skill_dir / "SKILL.md")
        assert fields.get("name") == skill_dir.name
        assert fields.get("description") is not None
        assert "version" not in fields


def test_generic_skills_do_not_depend_on_sports_ds_or_repo_root() -> None:
    forbidden = {
        "sports_ds import/reference": re.compile(r"\bsports_ds\b"),
        "sports-ds command/reference": re.compile(r"\bsports-ds(?!-bridge)\b"),
        "editable repo install": re.compile(r"pip\s+install\s+-e\s+\."),
        "repo-relative skill command": re.compile(r"python(?:3)?\s+skills/"),
        "cwd-relative helper command": re.compile(r"python(?:3)?\s+scripts/"),
    }
    text_suffixes = {".md", ".py", ".yaml", ".yml", ".json", ".toml"}

    for skill_dir in _skill_dirs():
        if skill_dir.name == BRIDGE:
            continue
        for path in skill_dir.rglob("*"):
            if not path.is_file() or path.suffix not in text_suffixes:
                continue
            text = path.read_text(encoding="utf-8")
            for label, pattern in forbidden.items():
                assert not pattern.search(text), f"{path} contains {label}"


def test_skill_scripts_parse_help_outside_repository(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    for script in sorted(SKILLS.glob("*/scripts/*.py")):
        proc = subprocess.run(
            [sys.executable, str(script), "--help"],
            cwd=tmp_path,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        assert proc.returncode == 0, (
            f"{script} --help failed with {proc.returncode}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def test_skill_scripts_compile() -> None:
    for script in sorted(SKILLS.glob("*/scripts/*.py")):
        source = script.read_text(encoding="utf-8")
        compile(source, str(script), "exec")
