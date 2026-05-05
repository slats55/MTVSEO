# Schema Engine Package

JSON-LD structured data generation and validation.

## Overview

Generates comprehensive JSON-LD schema markup for websites: Organization, LocalBusiness, WebSite, BreadcrumbList, Service, FAQPage, Article, and more. Validates schema syntax, checks for required properties, and auto-inserts markup into content drafts.

## Supported Schema Types

- Organization
- LocalBusiness (with subtypes: AutoRental, LegalService, etc.)
- WebSite (with SearchAction)
- BreadcrumbList
- Service
- FAQPage
- Article / BlogPosting
- Person
- ContactPage
- ImageObject

## Responsibilities

- Generate complete JSON-LD for all supported types
- Validate JSON-LD syntax and required properties
- Check schema against Google's Rich Results guidelines
- Auto-insert schema into HTML content drafts
- Generate standalone schema JSON files for manual insertion
- Track schema version history per page

## Key Classes / Functions

- `SchemaGenerator` — main schema factory
- `OrganizationSchema` — generates Organization / LocalBusiness schemas
- `WebsiteSchema` — generates WebSite schema with SearchAction
- `BreadcrumbSchema` — generates breadcrumb list from URL path
- `ArticleSchema` — generates Article / BlogPosting schema
- `FaqSchema` — generates FAQPage schema from Q&A pairs
- `SchemaValidator` — validates JSON-LD syntax and completeness
- `SchemaInserter` — injects schema into HTML documents

## Dependencies

- pydantic
- html.parser (stdlib)
- packages.shared
