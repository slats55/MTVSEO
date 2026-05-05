"""BriefGenerator — creates a full ContentBrief from keyword + business profile.

No DB dependency. Pure Pydantic-style dataclass composition.
"""

from datetime import datetime, timezone
import re
import slugify as slug_lib

from packages.content_engine.models import (
    BusinessContext,
    ContentBrief,
    ContentFormat,
    ContentGoal,
    InternalLinkOpportunity,
    KeywordCluster,
    KeywordSpec,
    OutlineSpec,
    ProofSource,
    ProofSource,
    SearchIntent,
    SectionSpec,
    Tone,
)


def _slugify(text: str) -> str:
    return slug_lib.slugify(text, lowercase=True, max_length=60)


def _default_cta(business: BusinessContext, goal: ContentGoal) -> str:
    if goal == ContentGoal.CONVERT:
        return "Request a Quote"
    elif goal == ContentGoal.RANK:
        return "Learn More"
    return "Contact Us"


def _schema_type_for_format(fmt: ContentFormat) -> str:
    mapping = {
        ContentFormat.FAQ_PAGE: "FAQPage",
        ContentFormat.SERVICE_PAGE: "Service",
        ContentFormat.BLOG_POST: "Article",
        ContentFormat.LANDING_PAGE: "WebPage",
        ContentFormat.PRODUCT_PAGE: "Product",
        ContentFormat.GUIDE: "Article",
        ContentFormat.CASE_STUDY: "Article",
        ContentFormat.ABOUT_PAGE: "AboutPage",
        ContentFormat.CONTACT_PAGE: "ContactPage",
    }
    return mapping.get(fmt, "Article")


def _outline_for_intent_and_format(
    intent: SearchIntent,
    fmt: ContentFormat,
    primary_kw: str,
) -> OutlineSpec:
    sections: list[SectionSpec] = []

    if fmt == ContentFormat.BLOG_POST or fmt == ContentFormat.GUIDE:
        sections = [
            SectionSpec(
                heading=f"What Is {primary_kw.title()}?",
                section_type="h2",
                purpose="Answer the searcher's primary question immediately",
                word_count_target=200,
                key_points=[
                    "Define the topic in one clear sentence",
                    "Establish why it matters to the reader",
                ],
            ),
            SectionSpec(
                heading="Why [Problem] Matters",
                section_type="h2",
                purpose="Build relevance and urgency",
                word_count_target=150,
                key_points=[
                    "Connect to audience pain points",
                    "Use a relatable scenario",
                ],
            ),
            SectionSpec(
                heading="How to [Achieve Outcome]",
                section_type="h2",
                purpose="Step-by-step guidance",
                word_count_target=400,
                key_points=[
                    "Numbered steps for actionable advice",
                    "Each step = one paragraph with a sub-point",
                ],
                internal_link_target=None,
                schema_to_include="HowTo" if intent == SearchIntent.INFORMATIONAL else None,
            ),
            SectionSpec(
                heading="Common Mistakes to Avoid",
                section_type="h2",
                purpose="Build authority and trust",
                word_count_target=150,
                key_points=[
                    "3-5 mistakes with brief explanations",
                    "Show what NOT to do and why",
                ],
            ),
            SectionSpec(
                heading="FAQ",
                section_type="ul",
                purpose="Capture informational intent and featured snippet opportunities",
                word_count_target=300,
                key_points=[
                    "5-7 common questions with direct answers",
                    "Each answer: 40-80 words",
                ],
                schema_to_include="FAQPage",
                has_faq_section=True,
                faq_count=6,
            ),
            SectionSpec(
                heading="Conclusion",
                section_type="h2",
                purpose="Summarize and drive next action",
                word_count_target=100,
                key_points=[
                    "1-paragraph summary",
                    "Clear CTA",
                ],
            ),
        ]
    elif fmt == ContentFormat.SERVICE_PAGE:
        sections = [
            SectionSpec(
                heading=f"Overview of Our {primary_kw.title()} Services",
                section_type="h2",
                purpose="Set context and establish expertise",
                word_count_target=150,
                key_points=["Service summary", "Years of experience", "Service area"],
                schema_to_include="Service",
            ),
            SectionSpec(
                heading="Signs You Need [Service]",
                section_type="h2",
                purpose="Trigger urgency and recognition",
                word_count_target=200,
                key_points=["5-7 signs with brief explanations"],
            ),
            SectionSpec(
                heading="Our [Service] Process",
                section_type="h2",
                purpose="Build trust with transparency",
                word_count_target=300,
                key_points=["Step-by-step numbered process", "What to expect"],
            ),
            SectionSpec(
                heading="Service Area",
                section_type="h2",
                purpose="Geo-targeting signal",
                word_count_target=150,
                key_points=["Cities/areas served", "Response time"],
                schema_to_include="LocalBusiness",
            ),
            SectionSpec(
                heading="FAQ",
                section_type="ul",
                purpose="Address common objections",
                word_count_target=250,
                key_points=["Pricing questions", "Timeline questions", "Warranty questions"],
                schema_to_include="FAQPage",
                has_faq_section=True,
                faq_count=5,
            ),
        ]
    elif fmt == ContentFormat.FAQ_PAGE:
        sections = [
            SectionSpec(
                heading=f"[Topic] FAQ",
                section_type="h1",
                purpose="Directly answer top questions",
                word_count_target=100,
                key_points=["Short intro to topic area"],
            ),
            SectionSpec(
                heading="General Questions",
                section_type="h2",
                purpose="Answer general informational questions",
                word_count_target=400,
                key_points=["5-6 questions with direct answers"],
                schema_to_include="FAQPage",
                has_faq_section=True,
                faq_count=6,
            ),
            SectionSpec(
                heading="Technical Questions",
                section_type="h2",
                purpose="Answer deeper technical questions",
                word_count_target=300,
                key_points=["3-4 technical questions", "Include specs where relevant"],
                schema_to_include="FAQPage",
            ),
        ]
    else:
        # Generic outline
        sections = [
            SectionSpec(
                heading=f"Introduction to {primary_kw.title()}",
                section_type="h2",
                purpose="Hook the reader and set expectations",
                word_count_target=150,
                key_points=["Opening hook", "What the article covers"],
            ),
            SectionSpec(
                heading="Main Content",
                section_type="h2",
                purpose="Core information delivery",
                word_count_target=600,
                key_points=["3-5 key points", "Supporting evidence"],
            ),
            SectionSpec(
                heading="Conclusion",
                section_type="h2",
                purpose="Wrap up and CTA",
                word_count_target=100,
                key_points=["Summary", "CTA"],
            ),
        ]

    total_words = sum(s.word_count_target for s in sections)
    return OutlineSpec(
        sections=sections,
        total_word_count_target=total_words,
        has_faq_section=any(s.has_faq_section for s in sections),
        faq_count=next((s.faq_count for s in sections if s.has_faq_section), 0),
    )


def _build_internal_links(
    primary_kw: str,
    fmt: ContentFormat,
    business: BusinessContext,
) -> list[InternalLinkOpportunity]:
    links: list[InternalLinkOpportunity] = []

    # Link to services pages from blog posts
    if fmt in (ContentFormat.BLOG_POST, ContentFormat.GUIDE):
        for svc in (business.services or [])[:3]:
            links.append(
                InternalLinkOpportunity(
                    target_url=f"/services/{_slugify(svc)}",
                    target_anchor_text=f"our {svc.lower()} services",
                    justification=f"Contextual link to relevant service page while discussing {svc}",
                    link_type="contextual",
                )
            )
        links.append(
            InternalLinkOpportunity(
                target_url="/contact",
                target_anchor_text="contact us today",
                justification="CTA link to contact page",
                link_type="in-content",
            )
        )

    # Link to about from service pages
    if fmt == ContentFormat.SERVICE_PAGE:
        links.append(
            InternalLinkOpportunity(
                target_url="/about",
                target_anchor_text="learn about our team",
                justification="Build trust by linking to about page",
                link_type="contextual",
            )
        )
        links.append(
            InternalLinkOpportunity(
                target_url="/",
                target_anchor_text=f"{business.business_name}",
                justification="Brand mention link to homepage",
                link_type="contextual",
            )
        )

    return links


def _compliance_flags(business: BusinessContext, fmt: ContentFormat) -> list[str]:
    flags: list[str] = []
    if business.is_cannabis:
        flags.append("CANNABIS: Verify state legality before publication")
        flags.append("CANNABIS: Include age-gating notice if applicable")
        flags.append("CANNABIS: Do not make unverified health claims")
    if business.is_financial:
        flags.append("FINANCIAL: Disclose risks, past performance is not indicative of future results")
        flags.append("FINANCIAL: Include SEC/FINRA disclaimers if relevant")
    if business.is_health:
        flags.append("HEALTH: Include 'consult a professional' disclaimer for medical advice")
        flags.append("HEALTH: Do not make specific medical claims without citation")
    if business.is_legal:
        flags.append("LEGAL: Include jurisdiction disclaimer")
        flags.append("LEGAL: Flag for attorney review before publication")
    if fmt in (ContentFormat.SERVICE_PAGE, ContentFormat.LANDING_PAGE):
        flags.append("Ensure all service claims are verifiable")
    return flags


class BriefGenerator:
    """Builds a full ContentBrief from keyword + business context."""

    def run(
        self,
        primary_keyword: str,
        business_context: BusinessContext,
        secondary_keywords: list[str] | None = None,
        search_intent: SearchIntent = SearchIntent.INFORMATIONAL,
        content_format: ContentFormat = ContentFormat.BLOG_POST,
        content_goal: ContentGoal = ContentGoal.RANK,
        keyword_clusters: list[KeywordCluster] | None = None,
        target_audience: str | None = None,
        tone: Tone = Tone.PROFESSIONAL,
    ) -> ContentBrief:
        secondary = secondary_keywords or []

        # Slug from primary keyword
        slug = _slugify(primary_keyword)
        if content_format != ContentFormat.BLOG_POST:
            slug = f"{content_format.value}/{slug}"

        # Outline
        outline = _outline_for_intent_and_format(search_intent, content_format, primary_keyword)

        # Internal links
        internal_links = _build_internal_links(primary_keyword, content_format, business_context)

        # Compliance flags
        compliance_flags = _compliance_flags(business_context, content_format)

        # Human review for YMYL-adjacent topics
        needs_review = (
            business_context.is_cannabis
            or business_context.is_financial
            or business_context.is_health
            or business_context.is_legal
            or content_goal == ContentGoal.CONVERT
        )

        # Audience
        audience = target_audience or f"People searching for {primary_keyword} in {business_context.location}"

        # Word count estimate
        estimated_read_time = max(3, outline.total_word_count_target // 200)

        # Schema type
        schema_type = _schema_type_for_format(content_format)

        # CTA
        cta = _default_cta(business_context, content_goal)

        # Business facts
        facts = []
        if business_context.unique_selling_points:
            facts.extend(business_context.unique_selling_points[:3])
        if business_context.certifications:
            facts.append(f"Certified in: {', '.join(business_context.certifications[:2])}")
        if business_context.location:
            facts.append(f"Serving: {business_context.service_areas[0] if business_context.service_areas else business_context.location}")

        return ContentBrief(
            slug=slug,
            content_goal=content_goal,
            content_format=content_format,
            target_audience=audience,
            audience_pain_points=[
                f"Struggling to find reliable {primary_keyword} providers",
                f"Unclear on what quality {primary_keyword} costs",
                f"Worried about compliance and safety",
            ],
            audience_search_questions=[
                f"What is {primary_keyword}?",
                f"How do I choose a provider for {primary_keyword}?",
                f"What should I expect from {primary_keyword}?",
            ],
            primary_keyword=primary_keyword,
            secondary_keywords=secondary,
            keyword_clusters=keyword_clusters or [],
            search_intent=search_intent,
            intent_rationale=f"Search intent is {search_intent.value} — the audience is looking to {'learn about' if search_intent == SearchIntent.INFORMATIONAL else 'find a provider for' if search_intent == SearchIntent.TRANSACTIONAL else 'research'} {primary_keyword}",
            outline=outline,
            external_proof_sources=self._default_proof_sources(primary_keyword),
            internal_link_targets=internal_links,
            primary_cta=cta,
            cta_placement="end",
            recommended_schema_type=schema_type,
            schema_properties={},
            business_facts_to_include=facts,
            compliance_flags=compliance_flags,
            human_review_required=needs_review,
            tone=tone,
            style_notes=f"Use {tone.value} tone. Be specific — avoid generic phrases. Include real numbers, real timelines, real proof.",
            estimated_read_time_minutes=estimated_read_time,
            word_count_min=max(300, outline.total_word_count_target - 200),
            word_count_max=outline.total_word_count_target + 500,
        )

    def _default_proof_sources(self, keyword: str) -> list[ProofSource]:
        """Stub proof sources — replace with real citations in production."""
        return [
            ProofSource(
                url=f"https://en.wikipedia.org/wiki/{keyword.replace(' ', '_')}",
                source_name="Wikipedia",
                quote_snippet=None,
                relevance="high",
            ),
        ]
