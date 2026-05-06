"""CLI entry point for packages/schema_engine.

Usage:
    python -m packages.schema_engine org --name "My Business" --url https://example.com
    python -m packages.schema_engine local --name "My Business" --url https://example.com --street "123 Main St" --city "Roanoke" --state "VA" --postal 24019
    python -m packages.schema_engine website --name "My Site" --url https://example.com
    python -m packages.schema_engine service --name "HVAC Repair" --description "..." --provider "My Business"
    python -m packages.schema_engine faq --faqs-json faqs.json
    python -m packages.schema_engine article --headline "My Article" --author "John Doe" --date-published 2026-01-01
    python -m packages.schema_engine validate --schema-json schema.json
"""

import argparse
import json
import sys
from pathlib import Path

from ..models import SchemaType, ValidationResult
from ..validator import SchemaValidator
from ..generators import (
    OrganizationSchemaGenerator,
    LocalBusinessSchemaGenerator,
    WebSiteSchemaGenerator,
    ServiceSchemaGenerator,
    FAQSchemaGenerator,
    ArticleSchemaGenerator,
)


def cmd_org(args) -> None:
    gen = OrganizationSchemaGenerator()
    schema = gen.generate(name=args.name, url=args.url, description=args.description)
    _output(schema, args)


def cmd_local(args) -> None:
    gen = LocalBusinessSchemaGenerator()
    schema = gen.generate(
        name=args.name,
        url=args.url,
        street_address=args.street,
        city=args.city,
        state=args.state,
        postal_code=args.postal,
        phone=args.phone,
        description=args.description,
        price_range=args.price_range,
    )
    _output(schema, args)


def cmd_website(args) -> None:
    gen = WebSiteSchemaGenerator()
    schema = gen.generate(name=args.name, url=args.url, search_url=args.search_url)
    _output(schema, args)


def cmd_service(args) -> None:
    gen = ServiceSchemaGenerator()
    schema = gen.generate(
        name=args.name,
        description=args.description,
        provider_name=args.provider,
        provider_url=args.provider_url,
        price_range=args.price_range,
    )
    _output(schema, args)


def cmd_faq(args) -> None:
    faqs = json.loads(Path(args.faqs_json).read_text())
    gen = FAQSchemaGenerator()
    schema = gen.generate(faqs=faqs, url=args.url)
    _output(schema, args)


def cmd_article(args) -> None:
    gen = ArticleSchemaGenerator()
    schema = gen.generate(
        headline=args.headline,
        author_name=args.author,
        date_published=args.date_published,
        description=args.description,
        url=args.url,
        is_blog_post=args.blog,
    )
    _output(schema, args)


def cmd_validate(args) -> None:
    schema_data = json.loads(Path(args.schema_json).read_text())
    # Reconstruct SchemaContext
    from ..models import SchemaContext
    schema = SchemaContext(
        schema_type=SchemaType(schema_data.get("@type", "Organization")),
        data={k: v for k, v in schema_data.items() if not k.startswith("@")},
    )
    validator = SchemaValidator()
    result = validator.validate(schema)
    print(f"Valid: {result.is_valid}")
    for err in result.errors:
        print(f"  ERROR [{err.field_path}]: {err.message}")
    for warn in result.warnings:
        print(f"  WARNING [{warn.field_path}]: {warn.message}")


def _output(schema, args) -> None:
    ld = {"@context": "https://schema.org"}
    ld.update(schema.data)
    output = json.dumps(ld, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output)
        print(f"Schema written to {args.output}")
    else:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m packages.schema_engine")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("org")
    p.add_argument("--name", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--description")
    p.add_argument("--output", "-o")
    p.set_defaults(fn=cmd_org)

    p = sub.add_parser("local")
    p.add_argument("--name", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--street", required=True)
    p.add_argument("--city", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--postal", required=True)
    p.add_argument("--phone")
    p.add_argument("--description")
    p.add_argument("--price-range")
    p.add_argument("--output", "-o")
    p.set_defaults(fn=cmd_local)

    p = sub.add_parser("website")
    p.add_argument("--name", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--search-url")
    p.add_argument("--output", "-o")
    p.set_defaults(fn=cmd_website)

    p = sub.add_parser("service")
    p.add_argument("--name", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--provider-url")
    p.add_argument("--price-range")
    p.add_argument("--output", "-o")
    p.set_defaults(fn=cmd_service)

    p = sub.add_parser("faq")
    p.add_argument("--faqs-json", required=True)
    p.add_argument("--url")
    p.add_argument("--output", "-o")
    p.set_defaults(fn=cmd_faq)

    p = sub.add_parser("article")
    p.add_argument("--headline", required=True)
    p.add_argument("--author", required=True)
    p.add_argument("--date-published")
    p.add_argument("--description")
    p.add_argument("--url")
    p.add_argument("--blog", action="store_true")
    p.add_argument("--output", "-o")
    p.set_defaults(fn=cmd_article)

    p = sub.add_parser("validate")
    p.add_argument("--schema-json", required=True)
    p.set_defaults(fn=cmd_validate)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
