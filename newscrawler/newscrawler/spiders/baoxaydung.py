import scrapy
import re
from urllib.parse import urlparse


class BaoXayDungSpider(scrapy.Spider):

    name = "baoxaydung"
    start_urls = ["https://baoxaydung.vn/timelinelist/1922/1.htm",
                  "https://baoxaydung.vn/timelinelist/1927/1.htm"]
    MAX_ARTICLES = 1000

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
        parent_category = response.css(
            "div.line-cate-parrent a.category-name_ac::text"
        ).get(default="").strip()
        
        self.count += 1

        title = response.css(
            "h1.detail-title::text"
        ).get("").strip()

        author = response.css(
            'span[itemprop="name"]::text'
        ).get("").strip()

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

        if is_excluded:
            self.logger.debug(
                f"Skip (excluded): {title}"
            )
            return

        if not has_accident:
            self.logger.debug(
                f"Skip (no accident): {title}"
            )
            return

        # ==========================

        yield {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "url": response.url
        }