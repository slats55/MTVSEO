"""SEO Agent OS — Content Engine Package.

Generates SEO content briefs with target audience, search intent, keyword strategy,
internal link targets, proof sources, CTA, schema type, and business-specific facts.

Public API:
    from packages.content_engine import (
        BusinessContext,
        ContentBrief,
        KeywordSpec,
        KeywordCluster,
        SectionSpec,
        OutlineSpec,
        BriefGenerator,
        ContentPlanner,
        KeywordClusterer,
    )

Usage:
    from packages.content_engine import BriefGenerator, BusinessContext

    biz = BusinessContext(
        business_name="Mountain View HVAC",
        services=["HVAC repair", "AC installation"],
        unique_selling_points=["24/7 emergency service", "licensed & insured"],
        location="Roanoke, Virginia",
    )
    generator = BriefGenerator()
    brief = generator.run(
        primary_keyword="HVAC repair service",
        secondary_keywords=["AC repair near me", "emergency HVAC"],
        search_intent=SearchIntent.COMMERCIAL,
        business_context=biz,
    )
    print(brief.slug)
