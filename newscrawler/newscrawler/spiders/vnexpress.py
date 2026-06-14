import scrapy

class VNExpressSpider(scrapy.Spider):
    name = "vnexpress"

    start_urls = [
        "https://vnexpress.net/khoa-hoc-cong-nghe"
    ]

    MAX_ARTICLES = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.article_count = 0
        self.visited = set()

    def parse(self, response):

        if self.article_count >= self.MAX_ARTICLES:
            return

        # Lấy link bài báo
        article_links = response.xpath(
            '//h2[contains(@class,"title-news")]//a/@href | '
            '//h3[contains(@class,"title-news")]//a/@href | '
            '//h2[contains(@class,"title")]/a/@href'
        ).getall()

        # Loại bỏ trùng
        article_links = list(dict.fromkeys(article_links))

        self.logger.info(
            f"Found {len(article_links)} article links on {response.url}"
        )

        for url in article_links:

            if self.article_count >= self.MAX_ARTICLES:
                return

            if not url.startswith("https://vnexpress.net/"):
                continue

            if url in self.visited:
                continue

            self.visited.add(url)

            yield response.follow(
                url,
                callback=self.parse_article
            )

        # Tìm trang tiếp theo
        next_page = response.css(
            "a.next-page::attr(href)"
        ).get()

        if next_page and self.article_count < self.MAX_ARTICLES:
            yield response.follow(
                next_page,
                callback=self.parse
            )

    def parse_article(self, response):

        title = response.css(
            "h1.title-detail::text"
        ).get(default="").strip()

        date = response.css(
            "span.date::text"
        ).get(default="").strip()

        author = (
            response.css(
                "p.author_mail strong::text"
            ).get()
            or response.xpath(
                '//p[contains(@style,"text-align:right")]//strong/text()'
            ).get()
            or ""
        )

        author = author.strip()

        texts = response.css(
            "article.fck_detail p.Normal::text"
        ).getall()

        seen = set()
        clean_texts = []

        for text in texts:

            text = text.strip()

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)
            clean_texts.append(text)

        content = " ".join(clean_texts)
        if not content:
            return


        text = f"{title} {content}".lower()
        
        # ==========================

        if self.article_count >= self.MAX_ARTICLES:
            return

        self.article_count += 1

        self.logger.info(
            f"Accident Article {self.article_count}: {title}"
        )

        yield {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "url": response.url
        }
