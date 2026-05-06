"""Organization schema generator."""

from ..models import SchemaContext, SchemaType


class OrganizationSchemaGenerator:
    """Generates Organization JSON-LD."""

    def generate(
        self,
        name: str,
        url: str,
        logo_url: str | None = None,
        description: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        country: str = "US",
        latitude: float | None = None,
        longitude: float | None = None,
        same_as: list[str] | None = None,
    ) -> SchemaContext:
        data: dict = {
            "@type": SchemaType.ORGANIZATION.value,
            "name": name,
            "url": url,
        }
        if logo_url:
            data["logo"] = logo_url
        if description:
            data["description"] = description
        if email:
            data["email"] = email
        if phone:
            data["telephone"] = phone
        if same_as:
            data["sameAs"] = same_as

        # Address
        if street_address or city or state or postal_code:
            address: dict = {"@type": "PostalAddress", "addressCountry": country}
            if street_address:
                address["streetAddress"] = street_address
            if city:
                address["addressLocality"] = city
            if state:
                address["addressRegion"] = state
            if postal_code:
                address["postalCode"] = postal_code
            data["address"] = address

        # Geo
        if latitude is not None and longitude is not None:
            data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": latitude,
                "longitude": longitude,
            }

        return SchemaContext(schema_type=SchemaType.ORGANIZATION, data=data)
