# Docker Runbook

> ⚠️ **IMPORTANT**: Docker commands can be destructive. Follow these rules strictly. When in doubt, ask before acting.

## Checking Docker Availability

```bash
docker --version
docker compose version
```

If either fails, Docker is not available. Do not attempt to run Docker commands.

## Inspecting Docker/Compose Files

### Find Docker files in the repo:
```bash
find . -name "docker-compose*.yml" -o -name "docker-compose*.yaml"
find . -name "Dockerfile*" -not -path "./.venv/*" -not -path "./.git/*"
```

### Inspect a compose file without running anything:
```bash
docker compose config
```
This parses and validates the compose file without starting services.

### View services defined:
```bash
docker compose ps
```

### View logs without starting services:
```bash
docker compose logs
docker compose logs [service_name]
```

## Starting Services Safely

1. **Always validate first**:
   ```bash
   docker compose config
   ```

2. **Start services in detached mode**:
   ```bash
   docker compose up -d
   ```

3. **Verify services are running**:
   ```bash
   docker compose ps
   ```

4. **Check logs**:
   ```bash
   docker compose logs -f [service_name]
   ```

## Running Tests/Builds Inside Docker

If the project supports Docker-based testing:

```bash
# Build without cache (rarely needed)
docker compose build --no-cache

# Run a specific service's tests
docker compose run --rm [service_name] pytest
```

## Viewing Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs -f [service_name]

# Last N lines
docker compose logs --tail=100 [service_name]
```

## Forbidden Commands

The following are **FORBIDDEN** unless Myles explicitly approves:

| Command | Why Forbidden |
|---------|---------------|
| `docker system prune -a` | Deletes all unused images, containers, volumes |
| `docker volume prune` | Deletes all local volumes |
| `docker compose down -v` | Stops and removes containers, networks, volumes |
| `docker compose down` (without -v) | Removes containers/network (volumes survive) — still use caution |

## If Docker Is Unavailable

1. Do NOT attempt to force Docker to work
2. Document the absence in `05-KNOWN-ISSUES.md`
3. Proceed with non-Docker verification (Python syntax checks, direct pytest)
4. Report the limitation in your handoff

## Environment Variables

If `.env` or `.env.example` exists, check it before starting Docker:

```bash
cat .env.example
```

Ensure any required env vars are set in your environment before running `docker compose up`.

---

*Last updated by: Mr.R9 (setup task MULTICA-OBSIDIAN-BRAIN-SETUP-001)*