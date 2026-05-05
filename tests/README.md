# Tests

End-to-end and integration test suite for SEO Agent OS.

## Structure

```
tests/
  unit/            # Unit tests per package (pytest)
  integration/     # API endpoint tests (pytest + TestClient)
  e2e/             # Full workflow tests (Playwright)
  fixtures/        # Shared test fixtures and factories
  conftest.py      # pytest configuration and shared fixtures
```

## Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=services/api --cov=packages

# E2E tests
playwright test tests/e2e/
```

## Conventions

- Unit tests: `test_<package>_<module>.py`
- Integration tests: `test_api_<route>.py`
- E2E tests: `test_workflow_<name>.py`
- Use pytest fixtures from `conftest.py`
- Mock external APIs (Google, OpenAI) in unit tests
- Use real database (test schema) in integration tests
