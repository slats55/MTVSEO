"""Content planner — builds a content calendar from keyword clusters and business context.

Produces a prioritized list of content briefs to create, grouped by quarter/month.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .models import (
    BusinessContext,
    ContentFormat,
    ContentGoal,
    KeywordCluster,
    SearchIntent,
)


@dataclass
class ContentPlanEntry:
    month: str            # "2026-Q1", "2026-Q2", etc.
    topic: str            # the primary keyword / topic
    content_format: ContentFormat
    content_goal: ContentGoal
    primary_keyword: str
    secondary_keywords: list[str]
    search_intent: SearchIntent
    priority: int         # 1 = highest
    notes: str = ""
    status: str = "planned"   # "planned" / "in_progress" / "published"


@dataclass
class ContentPlan:
    business_name: str
    generated_at: str
    entries: list[ContentPlanEntry] = field(default_factory=list)
    total_briefs_planned: int = 0


def _rank_priority(
    intent: SearchIntent,
    goal: ContentGoal,
    cluster: KeywordCluster | None = None,
) -> int:
    """Lower number = higher priority. 1 is highest."""
    score = 0
    if intent == SearchIntent.COMMERCIAL:
        score -= 2
    elif intent == SearchIntent.TRANSACTIONAL:
        score -= 3
    if goal == ContentGoal.CONVERT:
        score -= 1
    if cluster and cluster.estimated_difficulty < 40:
        score -= 1   # easier to rank = higher priority
    return max(1, 5 + score)


class ContentPlanner:
    """Builds a prioritized content plan from keyword clusters and business context."""

    def run(
        self,
        keyword_clusters: list[KeywordCluster],
        business_context: BusinessContext,
        months_ahead: int = 3,
    ) -> ContentPlan:
        entries: list[ContentPlanEntry] = []
        now = datetime.now(timezone.utc)

        for cluster in keyword_clusters:
            # Map cluster intent to content format
            fmt = self._intent_to_format(cluster.search_intent)
            goal = ContentGoal.RANK if cluster.search_intent in (
                SearchIntent.INFORMATIONAL, SearchIntent.NAVIGATIONAL
            ) else ContentGoal.CONVERT

            priority = _rank_priority(cluster.search_intent, goal, cluster)

            entry = ContentPlanEntry(
                month=f"{now.year}-Q{(now.month - 1) // 3 + 1}",
                topic=cluster.pillar_keyword,
                content_format=fmt,
                content_goal=goal,
                primary_keyword=cluster.pillar_keyword,
                secondary_keywords=cluster.supporting_keywords,
                search_intent=cluster.search_intent,
                priority=priority,
                notes=f"Cluster ID: {cluster.cluster_id}; {len(cluster.supporting_keywords)} supporting keywords",
            )
            entries.append(entry)

        # Sort by priority then add
        entries.sort(key=lambda e: e.priority)
        total = len(entries)

        return ContentPlan(
            business_name=business_context.business_name,
            generated_at=now.isoformat(),
            entries=entries,
            total_briefs_planned=total,
        )

    @staticmethod
    def _intent_to_format(intent: SearchIntent) -> ContentFormat:
        mapping = {
            SearchIntent.INFORMATIONAL: ContentFormat.BLOG_POST,
            SearchIntent.NAVIGATIONAL: ContentFormat.SERVICE_PAGE,
            SearchIntent.COMMERCIAL: ContentFormat.SERVICE_PAGE,
            SearchIntent.TRANSACTIONAL: ContentFormat.SERVICE_PAGE,
        }
        return mapping.get(intent, ContentFormat.BLOG_POST)
