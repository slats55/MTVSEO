# Scripts

Utility scripts for SEO Agent OS maintenance and one-off tasks.

## Scripts

| Script | Purpose |
|---|---|
| `migrate_db.py` | Run Alembic migrations |
| `seed_demo.py` | Seed demo data for local development |
| `cleanup_storage.py` | Remove old crawl snapshots and reports |
| `export_report.py` | Export a specific report to PDF/HTML |
| `validate_schema.py` | Validate a JSON-LD schema file |
| `check_robots.py` | Check a site's robots.txt for AI crawler directives |

## Usage

```bash
cd scripts
python migrate_db.py --head

python seed_demo.py --business "MTV Tech Solutions"

python cleanup_storage.py --older-than 30
```

## Guidelines

- All scripts must be idempotent (safe to run multiple times)
- Scripts must log their actions clearly
- Scripts must have a `--help` or `-h` flag
- No script should auto-commit to git or push to GitHub
