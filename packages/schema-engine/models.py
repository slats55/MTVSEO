"""JSON-LD schema data models — no database dependency."""

from dataclass_wizard import field
from dataclasses import dataclass, field as _field
from enum import Enum
from typing import Optional


class SchemaType(str, Enum):
    ORGANIZATION = "Organization"
    LOCAL_BUSINESS = "LocalBusiness"
    WEBSITE = "WebSite"
    WEB_PAGE = "WebPage"
    BREADCRUMB_LIST = "BreadcrumbList"
    SERVICE = "Service"
    PRODUCT = "Product"
    FAQ_PAGE = "FAQPage"
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    PERSON = "Person"
    CONTACT_PAGE = "ContactPage"
    ABOUT_PAGE = "AboutPage"
    HOW_TO = "HowTo"
    COURSE = "Course"
    EVENT = "Event"
    VIDEO = "VideoObject"


@dataclass
class GeoCoordinates:
    latitude: float
    longitude: float


@dataclass
class PostalAddress:
    street_address: str = ""
    address_locality: str = ""    # City
    address_region: str = ""       # State
    postal_code: str = ""
    address_country: str = "US"   # ISO 3166-1 alpha-2


@dataclass
class OpeningHours:
    day_of_week: list[str] = _field(default_factory=list)  # "Monday", "Tuesday", ...
    opens: str = "09:00"
    closes: str = "17:00"
    description: str = ""


@dataclass
class SchemaField:
    """A single schema.org property-value pair."""
    property_name: str    # e.g. "name", "url", "price"
    value: str | float | bool | list | None
    value_type: str = "Text"   # "Text", "URL", "Number", "Boolean", "Date", "DateTime"


@dataclass
class SchemaContext:
    schema_type: SchemaType
    data: dict            # flat key-value pairs for the schema
    nested_schemas: list["SchemaContext"] = _field(default_factory=list)  # for nested entities


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class ValidationError:
    field_path: str          # e.g. "address.streetAddress"
    message: str
    severity: str = "error"  # "error" / "warning"


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[ValidationError] = _field(default_factory=list)
    warnings: list[ValidationError] = _field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)
