"""Content brief data models — no database dependency."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ContentGoal(str, Enum):
    RANK = "rank"           # SEO rankings
    CONVERT = "convert"     # Lead/customer conversion
    EDUCATE = "educate"     # Brand awareness / education
    SUPPORT = "support"     # Customer support


class ContentFormat(str, Enum):
    BLOG_POST = "blog_post"
    SERVICE_PAGE = "service_page"
    FAQ_PAGE = "faq_page"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    ABOUT_PAGE = "about_page"
    CONTACT_PAGE = "contact_page"
    GUIDE = "guide"          # long-form how-to guide
    CASE_STUDY = "case_study"


class SearchIntent(str, Enum):
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"


# ---------------------------------------------------------------------------
# Keyword models
# ---------------------------------------------------------------------------

@dataclass
class KeywordSpec:
    keyword: str
    intent: SearchIntent
    is_primary: bool = False
    monthly_volume: Optional[int] = None   # e.g. 1200
    difficulty: Optional[float] = None     # 0-100
    cpc: Optional[float] = None            # USD
    notes: str = ""


@dataclass
class KeywordCluster:
    cluster_id: str
    pillar_keyword: str
    supporting_keywords: list[str] = field(default_factory=list)
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    estimated_difficulty: float = 50.0


# ---------------------------------------------------------------------------
# Section / outline models
# ---------------------------------------------------------------------------

@dataclass
class SectionSpec:
    heading: str
    section_type: str          # "h2" / "h3" / "ul" / "numbered"
    purpose: str                # why this section exists
    word_count_target: int     # approximate target words
    key_points: list[str] = field(default_factory=list)
    internal_link_target: Optional[str] = None   # URL to link to
    schema_to_include: Optional[str] = None    # e.g. "FAQPage", "HowTo"


@dataclass
class OutlineSpec:
    sections: list[SectionSpec] = field(default_factory=list)
    total_word_count_target: int = 1500
    has_faq_section: bool = False
    faq_count: int = 5


# ---------------------------------------------------------------------------
# Business context
# ---------------------------------------------------------------------------

@dataclass
class BusinessContext:
    business_name: str
    tagline: str = ""
    location: str = ""
    phone: str = ""
    email: str = ""
    website_url: str = ""
    social_profiles: dict[str, str] = field(default_factory=dict)  # platform -> URL
    services: list[str] = field(default_factory=list)
    service_areas: list[str] = field(default_factory=list)
    unique_selling_points: list[str] = field(default_factory=list)   # what makes them different
    certifications: list[str] = field(default_factory=list)
    awards: list[str] = field(default_factory=list)
    # YMYL / regulated industry flags
    is_cannabis: bool = False
    is_financial: bool = False
    is_health: bool = False
    is_legal: bool = False
    compliance_notes: str = ""


# ---------------------------------------------------------------------------
# Content brief
# ---------------------------------------------------------------------------

@dataclass
class ProofSource:
    url: str
    source_name: str
    quote_snippet: Optional[str] = None
    relevance: str = "high"   # "high" / "medium" / "low"


@dataclass
class InternalLinkOpportunity:
    target_url: str
    target_anchor_text: str
    justification: str
    link_type: str = "contextual"   # "contextual" / "in-content" / "callout"


@dataclass
class ContentBrief:
    # Meta
    slug: str
    content_goal: ContentGoal
    content_format: ContentFormat
    # Audience
    target_audience: str                  # e.g. "Small business owners in rural Virginia"
    audience_pain_points: list[str] = field(default_factory=list)
    audience_search_questions: list[str] = field(default_factory=list)
    # Keywords
    primary_keyword: str = ""
    secondary_keywords: list[str] = field(default_factory=list)
    keyword_clusters: list[KeywordCluster] = field(default_factory=list)
    # Intent
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    intent_rationale: str = ""            # why this intent matches the audience
    # Outline
    outline: OutlineSpec = field(default_factory=OutlineSpec)
    # Proof / credibility
    external_proof_sources: list[ProofSource] = field(default_factory=list)
    internal_link_targets: list[InternalLinkOpportunity] = field(default_factory=list)
    # CTA
    primary_cta: str = ""                  # e.g. "Request a quote"
    cta_placement: str = "end"            # "end" / "sidebar" / "inline"
    # Schema
    recommended_schema_type: str = ""    # e.g. "Service", "FAQPage", "Article"
    schema_properties: dict = field(default_factory=dict)  # extra schema fields
    # Business facts
    business_facts_to_include: list[str] = field(default_factory=list)
    # Compliance
    compliance_flags: list[str] = field(default_factory=list)
    human_review_required: bool = False
    # Style
    tone: Tone = Tone.PROFESSIONAL
    style_notes: str = ""
    # Stats
    estimated_read_time_minutes: int = 5
    word_count_min: int = 800
    word_count_max: int = 2500
