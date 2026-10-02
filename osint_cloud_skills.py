#!/usr/bin/env python3
"""
OSINT Cloud Skills — searchable library of cloud OSINT investigation skills.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LIBRARY_PATH = ROOT / "skills" / "library.json"


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass


def load_library(path: Path = LIBRARY_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("library.json must be a JSON array")
    return data


def skill_text(skill: dict[str, Any]) -> str:
    parts = [
        skill.get("id", ""),
        skill.get("title", ""),
        skill.get("category", ""),
        skill.get("summary", ""),
        skill.get("objective", ""),
        " ".join(skill.get("tags", [])),
        " ".join(skill.get("providers", [])),
        " ".join(skill.get("tools", [])),
        " ".join(skill.get("queries", [])),
        " ".join(skill.get("steps", [])),
    ]
    return " ".join(parts).lower()


def filter_skills(
    skills: list[dict[str, Any]],
    query: str | None = None,
    tag: str | None = None,
    provider: str | None = None,
    category: str | None = None,
    level: str | None = None,
) -> list[dict[str, Any]]:
    results = skills
    if query:
        q = query.lower()
        results = [s for s in results if q in skill_text(s)]
    if tag:
        t = tag.lower()
        results = [s for s in results if t in [x.lower() for x in s.get("tags", [])]]
    if provider:
        p = provider.lower()
        results = [s for s in results if p in [x.lower() for x in s.get("providers", [])]]
    if category:
        c = category.lower()
        results = [s for s in results if s.get("category", "").lower() == c]
    if level:
        l = level.lower()
        results = [s for s in results if s.get("level", "").lower() == l]
    return results


def print_table(skills: list[dict[str, Any]]) -> None:
    if not skills:
        print("No skills matched.")
        return
    print(f"{'ID':<24} {'Level':<12} {'Category':<14} Title")
    print(f"{'-'*24} {'-'*12} {'-'*14} {'-'*40}")
    for s in skills:
        print(
            f"{s.get('id',''):<24} {s.get('level',''):<12} {s.get('category',''):<14} {s.get('title','')}"
        )
    print(f"\n{len(skills)} skill(s)")


def print_skill(skill: dict[str, Any]) -> None:
    print(f"# {skill.get('title')} ({skill.get('id')})")
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
    print(f"  {skill.get('ethics', 'Use only within authorized scope.')}")


def cmd_list(args: argparse.Namespace) -> int:
    skills = filter_skills(
        load_library(),
        query=args.query,
        tag=args.tag,
        provider=args.provider,
        category=args.category,
        level=args.level,
    )
    if args.json:
        print(json.dumps(skills, ensure_ascii=False, indent=2))
    else:
        print_table(skills)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    skills = load_library()
    key = args.id_or_title.lower()
    match = next(
        (
            s
            for s in skills
            if s.get("id", "").lower() == key or s.get("title", "").lower() == key
        ),
        None,
    )
    if not match:
        # fuzzy contains
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


def cmd_tags(args: argparse.Namespace) -> int:
    skills = load_library()
    tags: dict[str, int] = {}
    for s in skills:
        for tag in s.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1
    for tag, count in sorted(tags.items(), key=lambda x: (-x[1], x[0])):
        print(f"{tag:<20} {count}")
    return 0


def cmd_providers(args: argparse.Namespace) -> int:
    skills = load_library()
    providers: dict[str, int] = {}
    for s in skills:
        for p in s.get("providers", []):
            providers[p] = providers.get(p, 0) + 1
    for p, count in sorted(providers.items(), key=lambda x: (-x[1], x[0])):
        print(f"{p:<20} {count}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    skills = filter_skills(
        load_library(),
        query=args.query,
        tag=args.tag,
        provider=args.provider,
        category=args.category,
        level=args.level,
    )
    out = Path(args.output)
    if args.format == "md":
        lines = ["# OSINT Cloud Skills Export", ""]
        for s in skills:
            lines.append(f"## {s.get('title')} (`{s.get('id')}`)")
            lines.append("")
            lines.append(f"- **Level:** {s.get('level')}")
            lines.append(f"- **Category:** {s.get('category')}")
            lines.append(f"- **Providers:** {', '.join(s.get('providers', []))}")
            lines.append(f"- **Tags:** {', '.join(s.get('tags', []))}")
            lines.append("")
            lines.append(s.get("summary", ""))
            lines.append("")
            lines.append("### Steps")
            for i, step in enumerate(s.get("steps", []), 1):
                lines.append(f"{i}. {step}")
            lines.append("")
            if s.get("queries"):
                lines.append("### Queries")
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


def cmd_search(args: argparse.Namespace) -> int:
    args.query = args.text
    return cmd_list(args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="osint-cloud-skills",
        description="Searchable OSINT skills library focused on cloud investigation.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    def add_filters(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("-q", "--query", help="Free-text search")
        sp.add_argument("--tag", help="Filter by tag")
        sp.add_argument("--provider", help="Filter by cloud provider (aws/azure/gcp/...)")
        sp.add_argument("--category", help="Filter by category")
        sp.add_argument("--level", help="Filter by level (beginner/intermediate/advanced)")
        sp.add_argument("--json", action="store_true", help="JSON output")

    list_p = sub.add_parser("list", help="List skills")
    add_filters(list_p)
    list_p.set_defaults(func=cmd_list)

    search_p = sub.add_parser("search", help="Search skills by text")
    search_p.add_argument("text", help="Search text")
    search_p.add_argument("--tag")
    search_p.add_argument("--provider")
    search_p.add_argument("--category")
    search_p.add_argument("--level")
    search_p.add_argument("--json", action="store_true")
    search_p.set_defaults(func=cmd_search)

    show_p = sub.add_parser("show", help="Show one skill in detail")
    show_p.add_argument("id_or_title", help="Skill id or title")
    show_p.add_argument("--json", action="store_true")
    show_p.set_defaults(func=cmd_show)

    tags_p = sub.add_parser("tags", help="List all tags")
    tags_p.set_defaults(func=cmd_tags)

    prov_p = sub.add_parser("providers", help="List providers coverage")
    prov_p.set_defaults(func=cmd_providers)

    export_p = sub.add_parser("export", help="Export filtered skills to file")
    add_filters(export_p)
    export_p.add_argument("-o", "--output", required=True, help="Output path")
    export_p.add_argument("--format", choices=["json", "md"], default="md")
    export_p.set_defaults(func=cmd_export)

    return p


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
