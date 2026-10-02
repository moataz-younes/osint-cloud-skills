#!/usr/bin/env python3
"""OSINT Skills Library CLI (Python) — browse multi-section skill packs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
CATALOG_PATH = SKILLS_ROOT / "catalog.json"


def _stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_all_skills(section: str | None = None) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    sections = [section] if section else [s["id"] for s in load_catalog()["sections"]]
    for sec in sections:
        folder = SKILLS_ROOT / sec
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.json")):
            if path.name.startswith("_"):
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            data.setdefault("section", sec)
            skills.append(data)
    return skills


def text_blob(skill: dict[str, Any]) -> str:
    bits = [
        skill.get("id", ""),
        skill.get("title", ""),
        skill.get("section", ""),
        skill.get("category", ""),
        skill.get("summary", ""),
        skill.get("objective", ""),
        " ".join(skill.get("tags", [])),
        " ".join(skill.get("providers", [])),
        " ".join(skill.get("tools", [])),
        " ".join(skill.get("queries", [])),
        " ".join(skill.get("steps", [])),
    ]
    return " ".join(bits).lower()


def apply_filters(
    skills: list[dict[str, Any]],
    query: str | None = None,
    tag: str | None = None,
    provider: str | None = None,
    category: str | None = None,
    level: str | None = None,
    section: str | None = None,
) -> list[dict[str, Any]]:
    out = skills
    if section:
        out = [s for s in out if s.get("section") == section]
    if query:
        q = query.lower()
        out = [s for s in out if q in text_blob(s)]
    if tag:
        t = tag.lower()
        out = [s for s in out if t in [x.lower() for x in s.get("tags", [])]]
    if provider:
        p = provider.lower()
        out = [s for s in out if p in [x.lower() for x in s.get("providers", [])]]
    if category:
        c = category.lower()
        out = [s for s in out if s.get("category", "").lower() == c]
    if level:
        l = level.lower()
        out = [s for s in out if s.get("level", "").lower() == l]
    return out


def print_table(skills: list[dict[str, Any]]) -> None:
    if not skills:
        print("No skills matched.")
        return
    print(f"{'Section':<14} {'ID':<24} {'Level':<12} Title")
    print(f"{'-'*14} {'-'*24} {'-'*12} {'-'*40}")
    for s in skills:
        print(
            f"{s.get('section',''):<14} {s.get('id',''):<24} {s.get('level',''):<12} {s.get('title','')}"
        )
    print(f"\n{len(skills)} skill(s)")


def print_skill(skill: dict[str, Any]) -> None:
    print(f"# {skill.get('title')} ({skill.get('id')})")
    print(f"Section   : {skill.get('section')}")
    print(f"Level     : {skill.get('level')}")
    print(f"Category  : {skill.get('category')}")
    print(f"Providers : {', '.join(skill.get('providers', []))}")
    print(f"Tags      : {', '.join(skill.get('tags', []))}")
    print()
    print("Summary")
    print(f"  {skill.get('summary')}")
    print()
    print("Objective")
    print(f"  {skill.get('objective')}")
    print()
    print("Steps")
    for i, step in enumerate(skill.get("steps", []), 1):
        print(f"  {i}. {step}")
    print()
    if skill.get("queries"):
        print("Example queries / patterns")
        for q in skill["queries"]:
            print(f"  - {q}")
        print()
    if skill.get("tools"):
        print("Tools")
        print("  " + ", ".join(skill["tools"]))
        print()
    if skill.get("outputs"):
        print("Outputs")
        print("  " + ", ".join(skill["outputs"]))
        print()
    print("Ethics")
    print(f"  {skill.get('ethics')}")


def add_filters(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("-q", "--query")
    sp.add_argument("--tag")
    sp.add_argument("--provider")
    sp.add_argument("--category")
    sp.add_argument("--level")
    sp.add_argument("--section", help="Section id (cloud, people, social, ...)")
    sp.add_argument("--json", action="store_true")


def cmd_sections(_: argparse.Namespace) -> int:
    catalog = load_catalog()
    print(f"{catalog['name']} v{catalog['version']} — {catalog['skill_count']} skills\n")
    print(f"{'ID':<14} {'Count':<6} Title")
    print(f"{'-'*14} {'-'*6} {'-'*40}")
    for s in catalog["sections"]:
        print(f"{s['id']:<14} {s['skill_count']:<6} {s['title']}")
        print(f"{'':<14} {''}{s['description']}")
        print()
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    skills = apply_filters(
        load_all_skills(args.section),
        query=args.query,
        tag=args.tag,
        provider=args.provider,
        category=args.category,
        level=args.level,
        section=args.section,
    )
    if args.json:
        print(json.dumps(skills, ensure_ascii=False, indent=2))
    else:
        print_table(skills)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    args.query = args.text
    return cmd_list(args)


def cmd_show(args: argparse.Namespace) -> int:
    key = args.id_or_title.lower()
    skills = load_all_skills()
    match = next((s for s in skills if s.get("id", "").lower() == key or s.get("title", "").lower() == key), None)
    if not match:
        contains = [s for s in skills if key in s.get("id", "").lower() or key in s.get("title", "").lower()]
        if len(contains) == 1:
            match = contains[0]
        elif contains:
            print("Multiple matches:")
            print_table(contains)
            return 1
        else:
            print(f"Skill not found: {args.id_or_title}", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(match, ensure_ascii=False, indent=2))
    else:
        print_skill(match)
    return 0


def cmd_tags(_: argparse.Namespace) -> int:
    tallies: dict[str, int] = {}
    for s in load_all_skills():
        for tag in s.get("tags", []):
            tallies[tag] = tallies.get(tag, 0) + 1
    for tag, count in sorted(tallies.items(), key=lambda x: (-x[1], x[0])):
        print(f"{tag:<24} {count}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    skills = apply_filters(
        load_all_skills(args.section),
        query=args.query,
        tag=args.tag,
        provider=args.provider,
        category=args.category,
        level=args.level,
        section=args.section,
    )
    out = Path(args.output)
    if args.format == "md":
        lines = ["# OSINT Skills Export", ""]
        by_section: dict[str, list] = {}
        for s in skills:
            by_section.setdefault(s.get("section", "other"), []).append(s)
        for sec, items in by_section.items():
            lines.append(f"## Section: {sec}")
            lines.append("")
            for s in items:
                lines.append(f"### {s.get('title')} (`{s.get('id')}`)")
                lines.append("")
                lines.append(f"- **Level:** {s.get('level')}")
                lines.append(f"- **Category:** {s.get('category')}")
                lines.append(f"- **Tags:** {', '.join(s.get('tags', []))}")
                lines.append("")
                lines.append(s.get("summary", ""))
                lines.append("")
                lines.append("#### Steps")
                for i, step in enumerate(s.get("steps", []), 1):
                    lines.append(f"{i}. {step}")
                lines.append("")
                if s.get("queries"):
                    lines.append("#### Queries")
                    for q in s["queries"]:
                        lines.append(f"- `{q}`")
                    lines.append("")
                lines.append(f"**Ethics:** {s.get('ethics', '')}")
                lines.append("")
        out.write_text("\n".join(lines), encoding="utf-8")
    else:
        out.write_text(json.dumps(skills, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(skills)} skill(s) -> {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="osint-skills",
        description="Multi-section OSINT skills library (cloud, people, social, network, ...).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sec = sub.add_parser("sections", help="List library sections")
    sec.set_defaults(func=cmd_sections)

    list_p = sub.add_parser("list", help="List skills")
    add_filters(list_p)
    list_p.set_defaults(func=cmd_list)

    search_p = sub.add_parser("search", help="Search skills")
    search_p.add_argument("text")
    add_filters(search_p)
    search_p.set_defaults(func=cmd_search)

    show_p = sub.add_parser("show", help="Show one skill")
    show_p.add_argument("id_or_title")
    show_p.add_argument("--json", action="store_true")
    show_p.set_defaults(func=cmd_show)

    tags_p = sub.add_parser("tags", help="List tags")
    tags_p.set_defaults(func=cmd_tags)

    export_p = sub.add_parser("export", help="Export filtered skills")
    add_filters(export_p)
    export_p.add_argument("-o", "--output", required=True)
    export_p.add_argument("--format", choices=["json", "md"], default="md")
    export_p.set_defaults(func=cmd_export)

    return p


def main(argv: list[str] | None = None) -> int:
    _stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
