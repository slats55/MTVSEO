"""SEO Agent OS — Schema Engine Package.

Generates JSON-LD structured data for schema.org types:
Organization, LocalBusiness, WebSite, BreadcrumbList, Service, Product,
FAQPage, Article, BlogPosting, Person, HowTo, and more.

Public API:
    from packages.schema_engine import (
        SchemaContext,
        SchemaType,
        SchemaValidator,
        OrganizationSchemaGenerator,
        LocalBusinessSchemaGenerator,
        WebSiteSchemaGenerator,
        ServiceSchemaGenerator,
        FAQSchemaGenerator,
        ArticleSchemaGenerator,
    )

Usage:
    from packages.schema_engine import FAQSchemaGenerator

    gen = FAQSchemaGenerator()
    schema = gen.generate(faqs=[{"question": "What is SEO?", "answer": "SEO is..."}])
    print(schema.data)
