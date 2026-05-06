"""JSON-LD schema validator — validates generated schemas against schema.org rules.

Checks required properties, value types, URL formats, and cross-field consistency.
No external API calls.
"""

import re
from typing import Any

from ..models import (
    SchemaContext,
    SchemaType,
    ValidationError,
    ValidationResult,
)


# Required properties per schema type
_REQUIRED: dict[SchemaType, list[str]] = {
    SchemaType.ORGANIZATION: ["name", "url"],
    SchemaType.LOCAL_BUSINESS: ["name", "url", "address", "geo"],
    SchemaType.WEBSITE: ["name", "url"],
    SchemaType.WEB_PAGE: ["name", "url"],
    SchemaType.BREADCRUMB_LIST: ["itemListElement"],
    SchemaType.SERVICE: ["name", "provider"],
    SchemaType.PRODUCT: ["name"],
    SchemaType.FAQ_PAGE: ["mainEntity"],
    SchemaType.ARTICLE: ["headline", "author", "datePublished"],
    SchemaType.BLOG_POSTING: ["headline", "author", "datePublished"],
    SchemaType.PERSON: ["name"],
    SchemaType.CONTACT_PAGE: ["name", "url"],
    SchemaType.ABOUT_PAGE: ["name", "url"],
    SchemaType.HOW_TO: ["name", "step"],
    SchemaType.COURSE: ["name", "provider"],
    SchemaType.EVENT: ["name", "startDate"],
    SchemaType.VIDEO: ["name", "uploadDate"],
}

# URL fields that must be valid URLs
_URL_FIELDS = {
    "url", "logo", "image", "sameAs", "author.url", "publisher.url",
    "provider.url", "breadcrumb.url", "item.url",
}

# Email fields
_EMAIL_FIELDS = {"email", "contactPoint.email"}


def _is_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(re.match(r"^https?://", value))


def _is_email(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", value))


def _is_phone(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(re.match(r"^\+?[\d\s\-().]{7,20}$", value))


class SchemaValidator:
    """Validates a SchemaContext against schema.org rules."""

    def validate(self, schema: SchemaContext) -> ValidationResult:
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []

        # Check required fields
        schema_type = SchemaType(schema.schema_type)
        required = _REQUIRED.get(schema_type, [])
        for prop in required:
            if prop not in schema.data or schema.data.get(prop) in (None, "", []):
                errors.append(
                    ValidationError(
                        field_path=prop,
                        message=f"Required property '{prop}' is missing or empty for {schema_type.value}",
                        severity="error",
                    )
                )

        # Check URL fields
        for prop in schema.data:
            value = schema.data[prop]
            if value and isinstance(value, str) and any(uf in prop for uf in _URL_FIELDS):
                if not _is_url(value):
                    errors.append(
                        ValidationError(
                            field_path=prop,
                            message=f"Field '{prop}' should be a valid URL, got: {value[:50]}",
                            severity="error",
                        )
                    )

        # Check email fields
        for prop in schema.data:
            value = schema.data[prop]
            if value and isinstance(value, str) and any(ef in prop for ef in _EMAIL_FIELDS):
                if not _is_email(value):
                    warnings.append(
                        ValidationError(
                            field_path=prop,
                            message=f"Field '{prop}' should be a valid email, got: {value}",
                            severity="warning",
                        )
                    )

        # Check telephone format
        if "telephone" in schema.data:
            tel = schema.data["telephone"]
            if tel and not _is_phone(tel):
                warnings.append(
                    ValidationError(
                        field_path="telephone",
                        message=f"Phone number format may be invalid: {tel}",
                        severity="warning",
                    )
                )

        # Check price format for Product
        if schema_type == SchemaType.PRODUCT and "price" in schema.data:
            price = schema.data.get("price")
            currency = schema.data.get("priceCurrency", "USD")
            if price is not None:
                try:
                    float(price)
                except (ValueError, TypeError):
                    errors.append(
                        ValidationError(
                            field_path="price",
                            message=f"price must be numeric, got: {price}",
                            severity="error",
                        )
                    )
                if not currency:
                    errors.append(
                        ValidationError(
                            field_path="priceCurrency",
                            message="priceCurrency is required when price is set",
                            severity="error",
                        )
                    )

        # Check date formats for Article/BlogPosting
        if schema_type in (SchemaType.ARTICLE, SchemaType.BLOG_POSTING):
            for date_field in ("datePublished", "dateModified"):
                val = schema.data.get(date_field)
                if val and not re.match(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?", val):
                    errors.append(
                        ValidationError(
                            field_path=date_field,
                            message=f"{date_field} should be ISO 8601 format (YYYY-MM-DD), got: {val}",
                            severity="error",
                        )
                    )

        # Warnings for optional but recommended fields
        recommended = {
            SchemaType.ARTICLE: ["description", "image", "publisher"],
            SchemaType.BLOG_POSTING: ["description", "image", "publisher"],
            SchemaType.SERVICE: ["description", "areaServed", "hasOfferCatalog"],
            SchemaType.LOCAL_BUSINESS: ["openingHours", "telephone", "priceRange"],
            SchemaType.ORGANIZATION: ["logo", "contactPoint", "sameAs"],
        }
        for prop in recommended.get(schema_type, []):
            if prop not in schema.data:
                warnings.append(
                    ValidationError(
                        field_path=prop,
                        message=f"Recommended property '{prop}' is missing for {schema_type.value}",
                        severity="warning",
                    )
                )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
