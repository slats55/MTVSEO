"""Keyword clusterer — groups keywords by semantic similarity and search intent.

Simple TF-IDF-free clustering using keyword overlap and intent grouping.
No external API needed.
"""

from typing import Optional
import uuid

from .models import KeywordCluster, KeywordSpec, SearchIntent


# Stopwords to remove when computing overlap
_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "this", "that", "these",
    "those", "it", "its", "near", "me", "my", "your", "our", "us",
    "how", "what", "why", "when", "where", "who", "which", "best", "top",
    "near", "local", "cheap", "affordable", "good", "best", "near me",
}


def _tokens(keyword: str) -> set[str]:
    return {
        t.strip().lower()
        for t in keyword.replace("-", " ").replace("/", " ").split()
        if t.strip().lower() not in _STOPWORDS and len(t.strip()) > 2
    }


def _intent_from_keyword(keyword: str) -> SearchIntent:
    kw = keyword.lower()
    transactional = {"buy", "order", "price", "cost", "rent", "hire", "schedule", "book", "quote", "get"}
    commercial = {"review", "vs", "versus", "compare", "comparison", "alternative", "top", "best", "rating"}
    if any(t in kw for t in transactional):
        return SearchIntent.TRANSACTIONAL
    if any(t in kw for t in commercial):
        return SearchIntent.COMMERCIAL
    if any(t in kw for t in {"near", "local", "near me"}):
        return SearchIntent.COMMERCIAL
    return SearchIntent.INFORMATIONAL


def _overlap(a: KeywordSpec, b: KeywordSpec) -> float:
    """Jaccard similarity between two keywords."""
    ta = _tokens(a.keyword)
    tb = _tokens(b.keyword)
    if not ta or not tb:
        return 0.0
    intersection = len(ta & tb)
    union = len(ta | tb)
    return intersection / union if union > 0 else 0.0


class KeywordClusterer:
    """Groups KeywordSpecs into KeywordClusters using Jaccard similarity + intent grouping."""

    def run(
        self,
        keywords: list[KeywordSpec],
        min_overlap: float = 0.20,
        max_clusters: int | None = None,
    ) -> list[KeywordCluster]:
        if not keywords:
            return []

        # Assign intents if not set
        for kw in keywords:
            if kw.intent is None:
                kw.intent = _intent_from_keyword(kw.keyword)

        # Sort by primary first
        sorted_kws = sorted(keywords, key=lambda k: (not k.is_primary, k.keyword))

        clusters: list[KeywordCluster] = []
        assigned: set[int] = set()

        for i, kw in enumerate(sorted_kws):
            if i in assigned:
                continue

            # Start a new cluster with this keyword as the pillar
            cluster_keywords = [kw.keyword]
            assigned.add(i)

            # Find all unassigned keywords with sufficient overlap or same intent
            for j, other in enumerate(sorted_kws):
                if j in assigned:
                    continue
                if other.intent == kw.intent and _overlap(kw, other) >= min_overlap:
                    cluster_keywords.append(other.keyword)
                    assigned.add(j)

            # Cluster difficulty = average of members
            difficulty = sum(
                (k.difficulty or 50.0) for k in sorted_kws
                if k.keyword in cluster_keywords and k.difficulty is not None
            ) / len(cluster_keywords) if cluster_keywords else 50.0

            cluster = KeywordCluster(
                cluster_id=str(uuid.uuid4())[:8],
                pillar_keyword=kw.keyword,
                supporting_keywords=[k for k in cluster_keywords if k != kw.keyword],
                search_intent=kw.intent,
                estimated_difficulty=round(difficulty, 1),
            )
            clusters.append(cluster)

            if max_clusters and len(clusters) >= max_clusters:
                break

        # Sort clusters: primary keywords first, then by difficulty (easy first)
        clusters.sort(key=lambda c: (not any(kw.keyword == c.pillar_keyword and kw.is_primary for kw in keywords), c.estimated_difficulty))

        return clusters

    def add_clusters_to_keywords(
        self,
        keywords: list[KeywordSpec],
        clusters: list[KeywordCluster],
    ) -> list[KeywordSpec]:
        """Tag each keyword with its cluster_id."""
        kw_to_cluster: dict[str, str] = {}
        for cluster in clusters:
            kw_to_cluster[cluster.pillar_keyword] = cluster.cluster_id
            for kw in cluster.supporting_keywords:
                kw_to_cluster[kw] = cluster.cluster_id

        for kw in keywords:
            kw.cluster_id = kw_to_cluster.get(kw.keyword, "")

        return keywords
