from urllib import response

import scrapy

class VNExpressSpider(scrapy.Spider):
    name = "vnexpress"

    start_urls = [
        "https://vnexpress.net/thoi-su/giao-thong",
        "https://vnexpress.net/phap-luat",
        "https://vnexpress.net/thoi-su"
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


        # ==========================
        # BỘ LỌC TAI NẠN GIAO THÔNG
        # ==========================

        text = f"{title} {content}".lower()

        accident_keywords = [
            "tai nạn giao thông",
            "tai nạn liên hoàn",
            "va chạm",
            "tông",
            "tông vào",
            "đâm",
            "đâm vào",
            "đâm trực diện",
            "đối đầu",
            "đụng",
            "lật xe",
            "xe lao",
            "lao xuống vực",
            "lao vào",
            "mất lái",
            "xe cán",
            "xe cuốn",
            "bốc cháy",
            "cháy xe",
            "rơi xuống vực",
            "rơi xuống sông",
            "húc văng",
            "húc đổ",
            "kẹt trong cabin",
            "kẹt trong xe",
            "xe lật ngang",
            "xe lao lên vỉa hè",
            "xe lao vào nhà dân",
            "tai nạn",
            "xe khách lật",
            "container lật",
            "xe tải lật",
            "tránh xe",
            "húc",
            "va vào"
        ]

        exclude_keywords = [ 
            "điểm đen",
            "điểm đen tai nạn",
            "giảm tai nạn",
            "kéo giảm tai nạn",
            "phòng chống tai nạn",
            "ngăn ngừa tai nạn",
            "an toàn giao thông",
            "tháng an toàn giao thông",
            "đầu tư",
            "cao tốc mới",
            "cầu mới",
            "khởi công",
            "thông tư",
            "bộ xây dựng",
            "cục đường bộ",
            "sở xây dựng", 
            "thống kê", 
            "giảm tai nạn", 
            "phòng chống", 
            "ngăn ngừa", 
            "tuyên truyền", 
            "an toàn giao thông", 
            "quy hoạch", 
            "dự án", 
            "hạ tầng", 
            "nghị định", 
            "luật giao thông", 
            "xử phạt", 
            "quốc hội", 
            "bộ giao thông", 
            "bộ xây dựng" 
        ]

        has_accident = any(
            kw in text
            for kw in accident_keywords
        )

        is_excluded = any(
            kw in text
            for kw in exclude_keywords
        )

        # Loại bài chính sách/thống kê
        if is_excluded:
            self.logger.debug(
                f"Skip (excluded): {title}"
            )
            return

        # Không có dấu hiệu tai nạn
        if not has_accident:
            self.logger.debug(
                f"Skip (no accident): {title}"
            )
            return

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
