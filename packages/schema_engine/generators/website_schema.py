"""WebSite schema generator."""

from ..models import SchemaContext, SchemaType


class WebSiteSchemaGenerator:
    """Generates WebSite JSON-LD with optional searchAction."""

    def generate(
        self,
        name: str,
        url: str,
        search_url: str | None = None,   # e.g. "https://example.com/search?q={search_term_string}"
        language: str = "en-US",
    ) -> SchemaContext:
        data: dict = {
            "@type": SchemaType.WEBSITE.value,
            "name": name,
            "url": url,
            "inLanguage": language,
        }
        if search_url:
            data["potentialAction"] = {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": search_url,
                },
                "query-input": "required name=search_term_string",
            }

        return SchemaContext(schema_type=SchemaType.WEBSITE, data=data)
