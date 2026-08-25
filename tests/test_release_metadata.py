from __future__ import annotations

import json
from pathlib import Path
import re

import sports_ds
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
ALLOWED_MANIFEST_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
ALLOWED_SKILL_FIELDS = {"name", "description", "license", "allowed-tools", "metadata"}
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---", flags=re.DOTALL)


def project_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, flags=re.MULTILINE)
    assert match is not None
    return match.group(1)


def test_release_versions_are_aligned() -> None:
    version = project_version()
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert sports_ds.__version__ == version
    assert manifest["version"] == version
    assert f"## {version}" in changelog
    for skill_file in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        assert f'  version: "{version}"' in text, skill_file


def test_skill_frontmatter_is_valid_and_current() -> None:
    version = project_version()

    for skill_file in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        assert match is not None, skill_file
        frontmatter = yaml.safe_load(match.group(1))

        assert isinstance(frontmatter, dict), skill_file
        assert set(frontmatter) <= ALLOWED_SKILL_FIELDS, skill_file
        assert frontmatter.get("name") == skill_file.parent.name, skill_file
        assert SKILL_NAME.fullmatch(frontmatter["name"]), skill_file
        assert len(frontmatter["name"]) <= 64, skill_file
        assert isinstance(frontmatter.get("description"), str), skill_file
        assert 0 < len(frontmatter["description"].strip()) <= 1024, skill_file
        assert "<" not in frontmatter["description"], skill_file
        assert ">" not in frontmatter["description"], skill_file
        assert frontmatter.get("metadata", {}).get("version") == version, skill_file
        assert "[TODO:" not in text, skill_file


def test_public_plugin_manifest_uses_the_closed_v1_shape() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))

    assert manifest["$schema"] == SCHEMA
    assert manifest["name"] == ROOT.name
    assert set(manifest) <= ALLOWED_MANIFEST_FIELDS
    assert (ROOT / "skills").is_dir()
    assert list((ROOT / "skills").glob("*/SKILL.md"))


def test_readme_badges_match_public_release_metadata() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill_count = len(list((ROOT / "skills").glob("*/SKILL.md")))

    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert "img.shields.io/github/v/release/" in readme
    assert "img.shields.io/badge/license-MIT-yellow.svg" in readme
    assert f"img.shields.io/badge/skills-{skill_count}-" in readme
    assert "standard-Agent_Skills" in readme
    assert "standard-Agent_Plugins" in readme
    assert "skills.sh/b/" not in readme
