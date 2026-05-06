"""LocalBusiness schema generator — extends Organization with local business fields."""

from ..models import (
    GeoCoordinates,
    OpeningHours,
    PostalAddress,
    SchemaContext,
    SchemaType,
)


class LocalBusinessSchemaGenerator:
    """Generates LocalBusiness JSON-LD with required address + geo."""

    def generate(
        self,
        name: str,
        url: str,
        street_address: str,
        city: str,
        state: str,
        postal_code: str,
        country: str = "US",
        latitude: float | None = None,
        longitude: float | None = None,
        phone: str | None = None,
        email: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
        opening_hours: list[OpeningHours] | None = None,
        price_range: str | None = None,        # e.g. "$$"
        same_as: list[str] | None = None,
        area_served: list[str] | None = None,  # e.g. ["Roanoke, VA", "Salem, VA"]
        service_types: list[str] | None = None,
    ) -> SchemaContext:
        data: dict = {
            "@type": SchemaType.LOCAL_BUSINESS.value,
            "name": name,
            "url": url,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": street_address,
                "addressLocality": city,
                "addressRegion": state,
                "postalCode": postal_code,
                "addressCountry": country,
            },
        }
        if latitude is not None and longitude is not None:
            data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": latitude,
                "longitude": longitude,
            }
        if phone:
            data["telephone"] = phone
        if email:
            data["email"] = email
        if description:
            data["description"] = description
        if logo_url:
            data["image"] = logo_url
        if opening_hours:
            oh_strings = []
            for oh in opening_hours:
                if oh.day_of_week and oh.opens and oh.closes:
                    oh_strings.append(
                        f"{','.join(oh.day_of_week)} {oh.opens}-{oh.closes}"
                    )
            if oh_strings:
                data["openingHours"] = oh_strings
        if price_range:
            data["priceRange"] = price_range
        if same_as:
            data["sameAs"] = same_as
        if area_served:
            data["areaServed"] = area_served
        if service_types:
            data["hasOfferCatalog"] = {
                "@type": "OfferCatalog",
                "name": "Services",
                "itemListElement": [{"@type": "Offer", "itemOffered": s} for s in service_types],
            }

        return SchemaContext(schema_type=SchemaType.LOCAL_BUSINESS, data=data)
