"""Service schema generator."""

from packages.schema_engine.models import SchemaContext, SchemaType


class ServiceSchemaGenerator:
    """Generates Service JSON-LD."""

    def generate(
        self,
        name: str,
        description: str,
        provider_name: str,
        provider_url: str | None = None,
        area_served: list[str] | None = None,
        service_type: str | None = None,
        url: str | None = None,
        image_url: str | None = None,
        price_range: str | None = None,
        terms_of_service: str | None = None,
    ) -> SchemaContext:
        data: dict = {
            "@type": SchemaType.SERVICE.value,
            "name": name,
            "description": description,
            "provider": {
                "@type": "Organization",
                "name": provider_name,
            },
        }
        if provider_url:
            data["provider"]["url"] = provider_url
        if area_served:
            data["areaServed"] = area_served
        if service_type:
            data["serviceType"] = service_type
        if url:
            data["url"] = url
        if image_url:
            data["image"] = image_url
        if price_range:
            data["priceRange"] = price_range
        if terms_of_service:
            data["termsOfService"] = terms_of_service

        return SchemaContext(schema_type=SchemaType.SERVICE, data=data)
