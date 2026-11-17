"""Versioned role and skill metadata layered on the existing JSON skill lists."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object
    )


def normalize_label(value):
    return " ".join(str(value or "").strip().lower().split())


def load_catalog():
    return read_json(ROOT / "role_catalog.json")


def resolve_role(value):
    label = normalize_label(value)
    for role in load_catalog()["roles"]:
        if label in {role["id"], role["name"], *role["aliases"]}:
            return role
    return None


def canonical_role_name(value):
    role = resolve_role(value)
    return role["name"] if role else normalize_label(value)


def validate_catalog():
    taxonomy = read_json(ROOT / "skills_taxonomy.json")
    profiles = read_json(ROOT / "roles.json")
    metadata = read_json(ROOT / "skill_metadata.json")["skills"]
    skills = set(taxonomy)
    aliases = {}
    for skill, names in taxonomy.items():
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate skill alias: {skill}")
        for alias in {skill, *names}:
            normalized = normalize_label(alias)
            if not normalized or normalized in aliases and aliases[normalized] != skill:
                raise ValueError(f"Ambiguous skill alias: {normalized}")
            aliases[normalized] = skill
    if {item["name"] for item in metadata} != skills or len(metadata) != len(skills):
        raise ValueError("Skill metadata must cover each canonical skill exactly once")
    if len({item["id"] for item in metadata}) != len(metadata):
        raise ValueError("Duplicate skill identifier")
    for item in metadata:
        for related in item["prerequisites"] + item["related_concepts"]:
            if related not in skills or related == item["name"]:
                raise ValueError(f"Invalid skill relationship: {related}")
    roles = load_catalog()["roles"]
    if len({role["id"] for role in roles}) != len(roles) or {
        r["name"] for r in roles
    } != set(profiles):
        raise ValueError("Role identifiers/profiles are inconsistent")
    role_aliases = set()
    for role in roles:
        names = {role["id"], role["name"], *role["aliases"]}
        if names & role_aliases:
            raise ValueError("Ambiguous role alias")
        role_aliases.update(names)
        assigned = role["required"] + role["recommended"] + role["advanced"]
        if len(assigned) != len(set(assigned)) or set(assigned) - skills:
            raise ValueError(f"Invalid skill classification: {role['id']}")
        if role["required"] != profiles[role["name"]] or not role["required"]:
            raise ValueError(
                "Default matching denominator does not match required skills"
            )
        if set(role["experience_expectations"]) != {
            "internship",
            "fresher",
            "intermediate",
            "experienced",
        }:
            raise ValueError("Missing experience expectations")
    return {
        "roles": len(roles),
        "skills": len(skills),
        "taxonomy_version": load_catalog()["taxonomy_version"],
    }
