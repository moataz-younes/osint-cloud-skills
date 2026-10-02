<div align="center">

# OSINT Cloud Skills

**A searchable skills library for Cloud OSINT investigations**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Deps](https://img.shields.io/badge/dependencies-none-success)](#)

Curated playbooks for investigating AWS / Azure / GCP / SaaS footprints using **public sources only**.

[Skills](#whats-inside) · [Install](#install) · [Usage](#usage) · [Ethics](#ethics)

</div>

---

## Why this exists

Cloud investigations need repeatable skills — not random Google tabs.  
This repo is a **personal OSINT skills library** you can search, filter, and export during cases.

## What's inside

12 ready skills across:

- Organization & stack recon  
- Certificate Transparency discovery  
- Public storage OSINT (responsible)  
- GitHub cloud-config OSINT  
- DNS / CDN provider mapping  
- Azure tenant clues  
- AWS / GCP public footprint patterns  
- Leak monitoring & incident OSINT  
- Wayback historical cloud assets  

Each skill includes: summary, objective, steps, example queries, tools, outputs, and ethics note.

## Install

```bash
git clone https://github.com/moataz-younes/osint-cloud-skills.git
cd osint-cloud-skills
python osint_cloud_skills.py --help
```

> Requires **Python 3.10+** · zero third-party dependencies

## Usage

```bash
# List all skills
python osint_cloud_skills.py list

# Search
python osint_cloud_skills.py search bucket
python osint_cloud_skills.py list --provider aws
python osint_cloud_skills.py list --tag github --level intermediate

# Show one skill
python osint_cloud_skills.py show public-bucket-osint
python osint_cloud_skills.py show "Certificate Transparency for Cloud Hosts"

# Browse tags / providers
python osint_cloud_skills.py tags
python osint_cloud_skills.py providers

# Export a filtered pack for a casefile
python osint_cloud_skills.py export --provider azure --format md -o azure-osint-pack.md
python osint_cloud_skills.py export --tag leak --format json -o leak-skills.json
```

## Add your own skills

Edit `skills/library.json` and append an object:

```json
{
  "id": "my-skill-id",
  "title": "My Cloud OSINT Skill",
  "category": "reconnaissance",
  "level": "beginner",
  "providers": ["aws"],
  "tags": ["custom"],
  "summary": "Short summary",
  "objective": "What success looks like",
  "steps": ["Step 1", "Step 2"],
  "queries": ["example query"],
  "tools": ["tool-a"],
  "outputs": ["notes"],
  "ethics": "Authorized use only."
}
```

## Ethics

This library is for **authorized investigations, defense, education, and research**.  
It focuses on public-source methods and responsible disclosure — not unauthorized access.

## Author

**Moataz Younes** — Cybercrime Investigator · OSINT · Cybersecurity  
GitHub: [moataz-younes](https://github.com/moataz-younes)

## License

MIT — see [LICENSE](LICENSE)
