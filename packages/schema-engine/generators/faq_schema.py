"""FAQPage schema generator."""

from packages.schema_engine.models import SchemaContext, SchemaType


class FAQSchemaGenerator:
    """Generates FAQPage JSON-LD."""

    def generate(
        self,
        faqs: list[dict],  # list of {"question": str, "answer": str}
        url: str | None = None,
    ) -> SchemaContext:
        main_entity = []
        for faq in faqs:
            q = faq.get("question", "")
            a = faq.get("answer", "")
            if q and a:
                main_entity.append({
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a,
                    },
                })

        data: dict = {
            "@type": SchemaType.FAQ_PAGE.value,
            "mainEntity": main_entity,
        }
        if url:
            data["url"] = url

        return SchemaContext(schema_type=SchemaType.FAQ_PAGE, data=data)
