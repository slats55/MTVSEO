# packages/geo-audit/analyzers/crawler_checker.py
"""Check AI crawler access via robots.txt directives.

Detects: GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Common Crawl.
Reports which are allowed, blocked, or unspecified.
"""

from urllib.parse import urlparse

from packages.crawler.models import PageRecord
from packages.geo_audit.models import GeoIssue, GeoIssueCategory, GeoIssueSeverity


# Well-known AI / search crawlers
AI_CRAWLERS = {
    "GPTBot": "OpenAI GPT-5 / GPT-4.5 web crawler",
    "ChatGPT-User": "ChatGPT user-facing plugin crawler",
    "ClaudeBot": "Anthropic Claude web crawler",
    "PerplexityBot": "Perplexity AI search crawler",
    "Google-Extended": "Google Gemini access to site content",
    "CCBot": "Common Crawl archive bot",
    "Bytespider": "Moz Bytespider",
    "Amazonbot": "Amazon AI search crawler",
    "OAI-SearchBot": "OpenAI SearchBot",
    "DuckDuckBot": "DuckDuckGo AI answers crawler",
}

# Good bots that should generally be allowed
GOOD_BOTS = {"GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "OAI-SearchBot", "DuckDuckBot"}
# Bots that might block AI training but are OK for search
AMBOT_BOTS = {}


def analyze(robots_txt_content: str | None) -> list[GeoIssue]:
    """Analyze robots.txt for AI crawler directives.

    Args:
        robots_txt_content: raw robots.txt text, or None if fetch failed

    Returns:
        list of GeoIssues for AI crawler access
    """
    issues: list[GeoIssue] = []
    if not robots_txt_content:
        # No robots.txt — all crawlers can access everything (fail open)
        issues.append(
            GeoIssue(
                issue_type="no_robots_txt",
                category=GeoIssueCategory.AI_CRAWLER_ACCESS,
                severity=GeoIssueSeverity.INFO,
                title="No robots.txt found",
                description=(
                    "The site has no robots.txt file. All AI crawlers (GPTBot, ClaudeBot, "
                    "PerplexityBot, etc.) can access all URLs freely. "
                    "This is generally fine, but provides no explicit guidance to crawlers."
                ),
                recommendation=(
                    "Consider adding a robots.txt file that explicitly allows friendly AI crawlers "
                    "and blocks only malicious bots. This gives you control over AI training access."
                ),
                affected_element="/robots.txt",
            )
        )
        return issues

    lines = robots_txt_content.splitlines()
    # Parse user-agent → rules mapping (simple approach)
    rules: dict[str, list[str]] = {}
    current_agent: str | None = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("user-agent:"):
            current_agent = line.split(":", 1)[1].strip().lower()
            if current_agent not in rules:
                rules[current_agent] = []
        elif line.lower().startswith("disallow:") and current_agent:
            rule = line.split(":", 1)[1].strip()
            rules[current_agent].append(f"DISALLOW: {rule}")
        elif line.lower().startswith("allow:") and current_agent:
            rule = line.split(":", 1)[1].strip()
            rules[current_agent].append(f"ALLOW: {rule}")

    # Check each AI crawler
    for agent_lower, agent_rules in rules.items():
        for crawler_name in AI_CRAWLERS:
            if crawler_name.lower() == agent_lower:
                rules_str = "; ".join(agent_rules) if agent_rules else "no rules (allows all)"
                if any("DISALLOW" in r for r in agent_rules):
                    issues.append(
                        GeoIssue(
                            issue_type=f"ai_crawler_blocked_{crawler_name}",
                            category=GeoIssueCategory.AI_CRAWLER_ACCESS,
                            severity=GeoIssueSeverity.HIGH,
                            title=f"{crawler_name} is blocked",
                            description=(
                                f"{crawler_name} ({AI_CRAWLERS[crawler_name]}) is blocked "
                                f"in robots.txt. Rules: {rules_str}. "
                                "This prevents that AI system from using your content in responses."
                            ),
                            recommendation=(
                                f"If you want your content used by {crawler_name}, "
                                f"remove the Disallow rule for {crawler_name} from robots.txt. "
                                "If you want to block AI training but allow search indexing, "
                                "use the AI-Owl protocol or a specific AI training block."
                            ),
                            affected_element=f"robots.txt: {crawler_name}",
                        )
                    )
                else:
                    issues.append(
                        GeoIssue(
                            issue_type=f"ai_crawler_allowed_{crawler_name}",
                            category=GeoIssueCategory.AI_CRAWLER_ACCESS,
                            severity=GeoIssueSeverity.INFO,
                            title=f"{crawler_name} is allowed",
                            description=(
                                f"{crawler_name} ({AI_CRAWLERS[crawler_name]}) is allowed "
                                "(no disallow rules). Your content can be used by this AI."
                            ),
                            recommendation="No action needed.",
                            affected_element=f"robots.txt: {crawler_name}",
                        )
                    )

    # Global * disallow (catch-all)
    if "*" in rules:
        global_rules = rules["*"]
        if any("DISALLOW" in r for r in global_rules):
            issues.append(
                GeoIssue(
                    issue_type="global_disallow_star",
                    category=GeoIssueCategory.AI_CRAWLER_ACCESS,
                    severity=GeoIssueSeverity.INFO,
                    title="Global Disallow: * in robots.txt",
                    description=(
                        "A 'Disallow: *' rule exists for User-Agent: * in robots.txt. "
                        "This may block some bots that don't match specific user-agent rules."
                    ),
                    recommendation=(
                        "Ensure this is intentional. If specific AI crawlers need access, "
                        "add explicit Allow rules for them above the global Disallow."
                    ),
                    affected_element="robots.txt: User-Agent: *",
                )
            )

    return issues
