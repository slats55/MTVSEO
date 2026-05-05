# SEO Agent OS — Schema Engine Package

Generates JSON-LD structured data for all major schema.org types.

---

## Architecture

```
packages/schema_engine/
  models.py                        # SchemaContext, SchemaType, ValidationResult, field models
  validator.py                     # SchemaValidator — validates required fields, URL/email formats
  generators/
    org_schema.py                  # OrganizationSchemaGenerator
    local_business_schema.py       # LocalBusinessSchemaGenerator
    website_schema.py              # WebSiteSchemaGenerator
    service_schema.py              # ServiceSchemaGenerator
    faq_schema.py                  # FAQSchemaGenerator
    article_schema.py              # ArticleSchemaGenerator / BlogPosting
    __init__.py
  __init__.py                    # Public API re-exports
  __main__.py                    # CLI entry point
  README.md                      # This file
```

---

## Public API

```python
from packages.schema_engine import (
    SchemaContext,
    SchemaType,
    SchemaValidator,
    ValidationResult,
    # Generators
    OrganizationSchemaGenerator,
    LocalBusinessSchemaGenerator,
    WebSiteSchemaGenerator,
    ServiceSchemaGenerator,
    FAQSchemaGenerator,
    ArticleSchemaGenerator,
)
```

---

## Usage

```python
# FAQPage schema
from packages.schema_engine import FAQSchemaGenerator

gen = FAQSchemaGenerator()
schema = gen.generate(faqs=[
    {"question": "What is HVAC maintenance?", "answer": "Regular HVAC maintenance..."},
])
print(schema.data)
# {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': '...', ...}]}
```

```python
# LocalBusiness schema
from packages.schema_engine import LocalBusinessSchemaGenerator, OpeningHours

gen = LocalBusinessSchemaGenerator()
schema = gen.generate(
    name="Mountain View HVAC",
    url="https://mtvhvac.com",
    street_address="123 Main St",
    city="Roanoke",
    state="VA",
    postal_code="24019",
    phone="+1-540-555-0100",
    price_range="$$",
    same_as=["https://facebook.com/mtvhvac"],
)
```

```python
# Article schema
from packages.schema_engine import ArticleSchemaGenerator

gen = ArticleSchemaGenerator()
schema = gen.generate(
    headline="How to Choose an HVAC Contractor",
    author_name="Mike Thompson",
    date_published="2026-05-01",
    url="https://mtvhvac.com/blog/choose-hvac-contractor",
)
```

```python
# Validate any schema
from packages.schema_engine import SchemaValidator

validator = SchemaValidator()
result = validator.validate(schema)
print(result.is_valid, result.error_count, result.warning_count)
```

### CLI

```bash
python -m packages.schema_engine faq --faqs-json faqs.json -o faq-schema.json

python -m packages.schema_engine local \
    --name "Mountain View HVAC" --url https://mtvhvac.com \
    --street "123 Main St" --city "Roanoke" --state "VA" --postal 24019 \
    --phone "+1-540-555-0100" --price-range "$$"

python -m packages.schema_engine validate --schema-json article-schema.json
```

---

## Supported Schema Types

| Type | Generator | Notes |
|------|-----------|-------|
| Organization | `OrganizationSchemaGenerator` | Base org schema with address, geo, sameAs |
| LocalBusiness | `LocalBusinessSchemaGenerator` | Requires address + geo; includes openingHours, areaServed |
| WebSite | `WebSiteSchemaGenerator` | Optional SearchAction for site search |
| Service | `ServiceSchemaGenerator` | provider, areaServed, priceRange |
| FAQPage | `FAQSchemaGenerator` | Converts question/answer pairs to Question + Answer |
| Article | `ArticleSchemaGenerator` | headline, author, datePublished, publisher |
| BlogPosting | `ArticleSchemaGenerator(is_blog_post=True)` | Same generator with BlogPosting type |

---

## Validation

SchemaValidator checks:
- **Required properties** per type (name, url, address, etc.)
- **URL format** for url/image/logo/sameAs fields
- **Email format** for email fields
- **Phone format** for telephone fields
- **Date format** (ISO 8601) for datePublished/dateModified
- **Recommended properties** (generates warnings)

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `packages/shared` | Exceptions, types |
