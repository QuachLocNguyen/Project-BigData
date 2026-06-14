import scrapy
import re

class BaoXayDungSpider(scrapy.Spider):

    name = "baoxaydung"
    start_urls = ["https://baoxaydung.vn/timelinelist/19210/1.htm",
                  "https://baoxaydung.vn/timelinelist/19253/1.htm",
                  "https://baoxaydung.vn/timelinelist/19254/1.htm",
                  "https://baoxaydung.vn/timelinelist/1922249/1.htm",
                  "https://baoxaydung.vn/timelinelist/19255/1.htm"]
    
    MAX_ARTICLES = 2000

    def __init__(self):
        self.count = 0
        self.visited = set()

    def parse(self, response):

        links = response.css(
            "a.box-category-link-title::attr(href)"
        ).getall()

        for link in links:
            yield response.follow(
                link,
                callback=self.parse_article
            )

        page = response.meta.get("page", 1)

        # Lấy category id từ URL hiện tại
        match = re.search(
            r"timelinelist/(\d+)/",
            response.url
        )

        if not match:
            return

        timeline_id = match.group(1)

        if page < 100:

            next_url = (
                f"https://baoxaydung.vn/"
                f"timelinelist/{timeline_id}/{page+1}.htm"
            )

            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={"page": page + 1}
            )

    def parse_article(self, response):
        categories = response.css(
            "div.line-cate-parrent a::text"
        ).getall()

        categories = [c.strip() for c in categories]

        if "Công nghệ" not in categories:
            return
        
        self.count += 1

        title = response.css(
            "h1.detail-title::text"
        ).get("").strip()

        author = (
            response.xpath(
                '//span[@data-role="name-author-item"]/text()'
            ).get()

            or response.xpath(
                '//span[@itemprop="name"]/text()'
            ).get()

            or response.xpath(
                '//p[contains(@class,"author_mail")]//strong/text()'
            ).get()

            or ""
        ).strip()

        date = response.css(
            'time[data-role="publishdate"]::text'
        ).get("").strip()

        content_section = response.xpath(
            '//section[@data-role="content"]'
        )

        paragraphs = []

        for p in content_section.xpath(
            './/p[not(descendant::img)]'
        ):

            text = " ".join(
                p.xpath('.//text()').getall()
            )

            text = re.sub(
                r'\s+',
                ' ',
                text
            ).strip()

            if len(text) < 20:
                continue

            if text.lower().startswith("ảnh"):
                continue

            if text.lower().startswith("video"):
                continue

            paragraphs.append(text)

        # Loại bỏ đoạn trùng
        seen = set()
        clean_paragraphs = []

        for para in paragraphs:
            if para not in seen:
                seen.add(para)
                clean_paragraphs.append(para)

        content = "\n".join(clean_paragraphs)

        if not title or not content:
            return

        text = f"{title} {content}".lower()
        
        # ==========================

        yield {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "url": response.url
        }