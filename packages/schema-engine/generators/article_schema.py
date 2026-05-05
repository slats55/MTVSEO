"""Article / BlogPosting schema generator."""

from packages.schema_engine.models import SchemaContext, SchemaType


class ArticleSchemaGenerator:
    """Generates Article or BlogPosting JSON-LD."""

    def generate(
        self,
        headline: str,
        author_name: str,
        author_url: str | None = None,
        date_published: str | None = None,   # "YYYY-MM-DD"
        date_modified: str | None = None,
        description: str | None = None,
        url: str | None = None,
        image_url: str | None = None,
        publisher_name: str | None = None,
        publisher_url: str | None = None,
        publisher_logo: str | None = None,
        is_blog_post: bool = False,
    ) -> SchemaContext:
        article_type = SchemaType.BLOG_POSTING if is_blog_post else SchemaType.ARTICLE
        data: dict = {
            "@type": article_type.value,
            "headline": headline,
            "author": {
                "@type": "Person",
                "name": author_name,
            },
        }
        if author_url:
            data["author"]["url"] = author_url
        if date_published:
            data["datePublished"] = date_published
        if date_modified:
            data["dateModified"] = date_modified
        if description:
            data["description"] = description
        if url:
            data["url"] = url
        if image_url:
            data["image"] = {"@type": "ImageObject", "url": image_url}
        if publisher_name:
            publisher: dict = {"@type": "Organization", "name": publisher_name}
            if publisher_url:
                publisher["url"] = publisher_url
            if publisher_logo:
                publisher["logo"] = {"@type": "ImageObject", "url": publisher_logo}
            data["publisher"] = publisher

        return SchemaContext(schema_type=article_type, data=data)
