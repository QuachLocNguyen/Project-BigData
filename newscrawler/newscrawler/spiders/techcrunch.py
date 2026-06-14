import re
import scrapy
import json
from datetime import datetime

class TechCrunchSpider(scrapy.Spider):
    name = "techcrunch"

    start_urls = [
        "https://techcrunch.com/latest/",
        "https://techcrunch.com/category/startups/",
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://techcrunch.com/category/apps/",
        "https://techcrunch.com/category/security/",
        "https://techcrunch.com/category/biotech-health/",
        "https://techcrunch.com/category/hardware/",
        "https://techcrunch.com/tag/cloud-computing/"
    ]

    MAX_ARTICLES = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.article_count = 0
        self.visited = set()

    def parse(self, response):

        if self.article_count >= self.MAX_ARTICLES:
            return

        article_links = []

        for href in response.css("a::attr(href)").getall():

            url = response.urljoin(href).split("#")[0]

            if re.search(r"/20\d{2}/\d{2}/\d{2}/", url):
                article_links.append(url)

        article_links = list(dict.fromkeys(article_links))

        self.logger.info(
            f"Found {len(article_links)} articles"
        )

        for url in article_links:

            if self.article_count >= self.MAX_ARTICLES:
                return

            if not url.startswith(
                "https://techcrunch.com/"
            ):
                continue

            if url in self.visited:
                continue

            self.visited.add(url)

            yield response.follow(
                url,
                callback=self.parse_article
            )

        next_page = response.xpath(
            '//a[contains(@class,"wp-block-query-pagination-next")]/@href'
        ).get()

        if next_page and self.article_count < self.MAX_ARTICLES:

            yield response.follow(
                next_page,
                callback=self.parse
            )

    def parse_article(self, response):

        data = {}

        scripts = response.xpath(
            '//script[@type="application/ld+json"]/text()'
        ).getall()

        for script in scripts:
            try:
                obj = json.loads(script)

                if isinstance(obj, dict):

                    # Trường hợp @graph
                    if "@graph" in obj:
                        for item in obj["@graph"]:
                            if (
                                isinstance(item, dict)
                                and item.get("@type") == "NewsArticle"
                            ):
                                data = item
                                break

                    # Trường hợp thường
                    elif obj.get("@type") in [
                        "NewsArticle",
                        "Article"
                    ]:
                        data = obj

                if data:
                    break

            except Exception:
                continue

        title = data.get("headline", "")

        date = data.get("datePublished", "")

        description = response.css(
            'meta[name="description"]::attr(content)'
        ).get("")

        author = response.css(
            'meta[name="author"]::attr(content)'
        ).get("")

        paragraphs = [
            p.strip()
            for p in response.css(
                ".entry-content p"
            ).xpath("string(.)").getall()
            if p.strip()
        ]

        content = "\n\n".join(paragraphs)

        if description and description not in content:
            content = description + "\n\n" + content

        self.article_count += 1

        yield {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "url": response.url
        }