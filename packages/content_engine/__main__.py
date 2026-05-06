"""CLI entry point for packages/content_engine.

Usage:
    python -m packages.content_engine brief "HVAC repair service" --secondary "AC repair near me,emergency HVAC" --location "Roanoke, Virginia"
    python -m packages.content_engine cluster keywords.json
    python -m packages.content_engine plan clusters.json --business-name "Mountain View HVAC" --services "HVAC repair,AC installation"
"""

import argparse
import json
import sys
from pathlib import Path

from ..models import (
    BusinessContext,
    ContentFormat,
    ContentGoal,
    KeywordCluster,
    KeywordSpec,
    SearchIntent,
    Tone,
)
from ..brief_generator import BriefGenerator
from ..keyword_clusterer import KeywordClusterer
from ..content_planner import ContentPlanner


def cmd_brief(args) -> None:
    biz = BusinessContext(
        business_name=args.business_name or "Our Business",
        location=args.location or "",
        website_url=args.website_url or "",
        services=args.services or [],
        service_areas=args.service_areas or [],
        is_cannabis=args.is_cannabis,
    )
    secondary = [s.strip() for s in (args.secondary or "").split(",") if s.strip()]
    generator = BriefGenerator()
    brief = generator.run(
        primary_keyword=args.keyword,
        business_context=biz,
        secondary_keywords=secondary,
        search_intent=SearchIntent(args.intent) if args.intent else SearchIntent.INFORMATIONAL,
        content_format=ContentFormat(args.format) if args.format else ContentFormat.BLOG_POST,
        content_goal=ContentGoal(args.goal) if args.goal else ContentGoal.RANK,
    )
    output = json.dumps(brief, indent=2, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o))
    if args.output:
        Path(args.output).write_text(output)
        print(f"Brief written to {args.output}")
    else:
        print(output)


def cmd_cluster(args) -> None:
    keywords_data = json.loads(Path(args.keywords_file).read_text())
    keywords = [
        KeywordSpec(
            keyword=k.get("keyword", ""),
            intent=SearchIntent(k.get("intent", "informational")),
            is_primary=k.get("is_primary", False),
            monthly_volume=k.get("monthly_volume"),
            difficulty=k.get("difficulty"),
        )
        for k in keywords_data
    ]
    clusterer = KeywordClusterer()
    clusters = clusterer.run(keywords, min_overlap=args.min_overlap)
    output = json.dumps(
        [c for c in clusters],
        indent=2,
        default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o),
    )
    if args.output:
        Path(args.output).write_text(output)
        print(f"Clusters written to {args.output}")
    else:
        print(output)


def cmd_plan(args) -> None:
    clusters_data = json.loads(Path(args.clusters_file).read_text())
    clusters = [
        KeywordCluster(
            cluster_id=c.get("cluster_id", ""),
            pillar_keyword=c.get("pillar_keyword", ""),
            supporting_keywords=c.get("supporting_keywords", []),
            search_intent=SearchIntent(c.get("search_intent", "informational")),
            estimated_difficulty=c.get("estimated_difficulty", 50.0),
        )
        for c in clusters_data
    ]
    biz = BusinessContext(
        business_name=args.business_name or "Our Business",
        services=args.services or [],
        location=args.location or "",
    )
    planner = ContentPlanner()
    plan = planner.run(clusters, biz)
    output = json.dumps(plan, indent=2, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o))
    if args.output:
        Path(args.output).write_text(output)
        print(f"Plan written to {args.output}")
    else:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m packages.content_engine")
    sub = parser.add_subparsers(required=True)

    p_brief = sub.add_parser("brief", help="Generate a content brief")
    p_brief.add_argument("keyword")
    p_brief.add_argument("--secondary", help="Comma-separated secondary keywords")
    p_brief.add_argument("--intent", choices=["informational","navigational","commercial","transactional"])
    p_brief.add_argument("--format", choices=["blog_post","service_page","faq_page","landing_page"])
    p_brief.add_argument("--goal", choices=["rank","convert","educate","support"])
    p_brief.add_argument("--business-name", default="Our Business")
    p_brief.add_argument("--location", default="")
    p_brief.add_argument("--website-url", default="")
    p_brief.add_argument("--services", help="Comma-separated services")
    p_brief.add_argument("--service-areas", help="Comma-separated service areas")
    p_brief.add_argument("--is-cannabis", action="store_true")
    p_brief.add_argument("--output", "-o")
    p_brief.set_defaults(fn=cmd_brief)

    p_cluster = sub.add_parser("cluster", help="Cluster keywords into topic groups")
    p_cluster.add_argument("keywords_file")
    p_cluster.add_argument("--min-overlap", type=float, default=0.20)
    p_cluster.add_argument("--output", "-o")
    p_cluster.set_defaults(fn=cmd_cluster)

    p_plan = sub.add_parser("plan", help="Build a content plan from keyword clusters")
    p_plan.add_argument("clusters_file")
    p_plan.add_argument("--business-name", default="Our Business")
    p_plan.add_argument("--services", help="Comma-separated services")
    p_plan.add_argument("--location", default="")
    p_plan.add_argument("--output", "-o")
    p_plan.set_defaults(fn=cmd_plan)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
