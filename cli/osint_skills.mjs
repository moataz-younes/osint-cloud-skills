#!/usr/bin/env node
/**
 * OSINT Skills Library CLI (Node.js) — browse multi-section skill packs.
 * Usage: node cli/osint_skills.mjs <command>
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const SKILLS_ROOT = path.join(ROOT, "skills");
const CATALOG_PATH = path.join(SKILLS_ROOT, "catalog.json");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function loadCatalog() {
  return readJson(CATALOG_PATH);
}

function loadAllSkills(section) {
  const catalog = loadCatalog();
  const sections = section ? [section] : catalog.sections.map((s) => s.id);
  const skills = [];
  for (const sec of sections) {
    const folder = path.join(SKILLS_ROOT, sec);
    if (!fs.existsSync(folder)) continue;
    for (const name of fs.readdirSync(folder).sort()) {
      if (!name.endsWith(".json") || name.startsWith("_")) continue;
      const data = readJson(path.join(folder, name));
      data.section = data.section || sec;
      skills.push(data);
    }
  }
  return skills;
}

function blob(skill) {
  return [
    skill.id,
    skill.title,
    skill.section,
    skill.category,
    skill.summary,
    skill.objective,
    ...(skill.tags || []),
    ...(skill.providers || []),
    ...(skill.tools || []),
    ...(skill.queries || []),
    ...(skill.steps || []),
  ]
    .join(" ")
    .toLowerCase();
}

function filterSkills(skills, opts = {}) {
  let out = skills;
  if (opts.section) out = out.filter((s) => s.section === opts.section);
  if (opts.query) {
    const q = opts.query.toLowerCase();
    out = out.filter((s) => blob(s).includes(q));
  }
  if (opts.tag) {
    const t = opts.tag.toLowerCase();
    out = out.filter((s) => (s.tags || []).some((x) => x.toLowerCase() === t));
  }
  if (opts.provider) {
    const p = opts.provider.toLowerCase();
    out = out.filter((s) => (s.providers || []).some((x) => x.toLowerCase() === p));
  }
  if (opts.level) {
    const l = opts.level.toLowerCase();
    out = out.filter((s) => (s.level || "").toLowerCase() === l);
  }
  return out;
}

function printTable(skills) {
  if (!skills.length) {
    console.log("No skills matched.");
    return;
  }
  console.log(
    "Section".padEnd(14),
    "ID".padEnd(24),
    "Level".padEnd(12),
    "Title"
  );
  console.log("-".repeat(14), "-".repeat(24), "-".repeat(12), "-".repeat(40));
  for (const s of skills) {
    console.log(
      String(s.section || "").padEnd(14),
      String(s.id || "").padEnd(24),
      String(s.level || "").padEnd(12),
      s.title || ""
    );
  }
  console.log(`\n${skills.length} skill(s)`);
}

function printSkill(skill) {
  console.log(`# ${skill.title} (${skill.id})`);
  console.log(`Section   : ${skill.section}`);
  console.log(`Level     : ${skill.level}`);
  console.log(`Category  : ${skill.category}`);
  console.log(`Providers : ${(skill.providers || []).join(", ")}`);
  console.log(`Tags      : ${(skill.tags || []).join(", ")}`);
  console.log("\nSummary\n ", skill.summary);
  console.log("\nObjective\n ", skill.objective);
  console.log("\nSteps");
  (skill.steps || []).forEach((step, i) => console.log(`  ${i + 1}. ${step}`));
  if (skill.queries?.length) {
    console.log("\nExample queries / patterns");
    skill.queries.forEach((q) => console.log(`  - ${q}`));
  }
  if (skill.tools?.length) console.log("\nTools\n ", skill.tools.join(", "));
  if (skill.outputs?.length) console.log("\nOutputs\n ", skill.outputs.join(", "));
  console.log("\nEthics\n ", skill.ethics);
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith("-")) args[key] = true;
      else {
        args[key] = next;
        i++;
      }
    } else if (a.startsWith("-") && a.length === 2) {
      const map = { q: "query", o: "output", s: "section" };
      const key = map[a.slice(1)] || a.slice(1);
      args[key] = argv[++i];
    } else args._.push(a);
  }
  return args;
}

function help() {
  console.log(`OSINT Skills Library (Node.js)

Usage:
  node cli/osint_skills.mjs sections
  node cli/osint_skills.mjs list [--section cloud] [--tag dns] [--provider aws] [--level beginner] [-q text]
  node cli/osint_skills.mjs search <text> [--section social]
  node cli/osint_skills.mjs show <id-or-title>
  node cli/osint_skills.mjs tags
  node cli/osint_skills.mjs export -o out.md [--section cloud] [--format md|json]
`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];
  if (!cmd || cmd === "help" || args.help) {
    help();
    process.exit(0);
  }

  if (cmd === "sections") {
    const catalog = loadCatalog();
    console.log(`${catalog.name} v${catalog.version} — ${catalog.skill_count} skills\n`);
    for (const s of catalog.sections) {
      console.log(`${s.id.padEnd(14)} ${String(s.skill_count).padEnd(4)} ${s.title}`);
      console.log(`${"".padEnd(14)} ${s.description}\n`);
    }
    return;
  }

  if (cmd === "list" || cmd === "search") {
    if (cmd === "search") args.query = args._[1] || args.query;
    const skills = filterSkills(loadAllSkills(args.section), args);
    if (args.json) console.log(JSON.stringify(skills, null, 2));
    else printTable(skills);
    return;
  }

  if (cmd === "show") {
    const key = (args._[1] || "").toLowerCase();
    const skills = loadAllSkills();
    let match = skills.find(
      (s) => s.id.toLowerCase() === key || (s.title || "").toLowerCase() === key
    );
    if (!match) {
      const contains = skills.filter(
        (s) => s.id.toLowerCase().includes(key) || (s.title || "").toLowerCase().includes(key)
      );
      if (contains.length === 1) match = contains[0];
      else if (contains.length > 1) {
        console.log("Multiple matches:");
        printTable(contains);
        process.exit(1);
      } else {
        console.error(`Skill not found: ${args._[1]}`);
        process.exit(1);
      }
    }
    if (args.json) console.log(JSON.stringify(match, null, 2));
    else printSkill(match);
    return;
  }

  if (cmd === "tags") {
    const tallies = {};
    for (const s of loadAllSkills()) {
      for (const tag of s.tags || []) tallies[tag] = (tallies[tag] || 0) + 1;
    }
    Object.entries(tallies)
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .forEach(([tag, count]) => console.log(tag.padEnd(24), count));
    return;
  }

  if (cmd === "export") {
    if (!args.output) {
      console.error("Missing -o/--output");
      process.exit(2);
    }
    const skills = filterSkills(loadAllSkills(args.section), args);
    const format = args.format || "md";
    if (format === "json") {
      fs.writeFileSync(args.output, JSON.stringify(skills, null, 2), "utf8");
    } else {
      const lines = ["# OSINT Skills Export", ""];
      for (const s of skills) {
        lines.push(`## ${s.title} (\`${s.id}\`)`);
        lines.push("");
        lines.push(`- **Section:** ${s.section}`);
        lines.push(`- **Level:** ${s.level}`);
        lines.push(`- **Tags:** ${(s.tags || []).join(", ")}`);
        lines.push("");
        lines.push(s.summary || "");
        lines.push("");
        lines.push("### Steps");
        (s.steps || []).forEach((step, i) => lines.push(`${i + 1}. ${step}`));
        lines.push("");
      }
      fs.writeFileSync(args.output, lines.join("\n"), "utf8");
    }
    console.log(`Wrote ${skills.length} skill(s) -> ${args.output}`);
    return;
  }

  help();
  process.exit(2);
}

main();
