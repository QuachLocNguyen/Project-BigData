import json
import re
from datetime import datetime, timezone, timedelta
from html import unescape

def normalize_date(date_str):

    match = re.search(
        r'(\d{1,2})/(\d{1,2})/(\d{4}),\s*(\d{1,2}:\d{2})',
        date_str
    )

    if match:
        day, month, year, hour = match.groups()

        dt = datetime.strptime(
            f"{day}/{month}/{year} {hour}",
            "%d/%m/%Y %H:%M"
        )

        return dt.strftime("%Y-%m-%d %H:%M:%S")

    return date_str

def normalize_date_techcrunch(date_str):
    try:
        dt = datetime.fromisoformat(
            date_str.replace("Z", "+00:00")
        )

        vn_tz = timezone(timedelta(hours=7))

        dt = dt.astimezone(vn_tz)

        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return date_str

# Đọc VnExpress
with open(r"C:\Users\Huong Giang\Downloads\newscrawler\newscrawler\vnexpress.json", encoding="utf-8") as f:
    vnexpress = json.load(f)

# Chuẩn hóa ngày
for item in vnexpress:
    item["date"] = normalize_date(item["date"])

# Đọc Báo Xây Dựng
with open(r"C:\Users\Huong Giang\Downloads\newscrawler\newscrawler\baoxaydung.json", encoding="utf-8") as f:
    baoxaydung = json.load(f)

for item in baoxaydung:
    item["date"] = normalize_date(item["date"])

# Đọc TechCrunch
with open(r"C:\Users\Huong Giang\Downloads\newscrawler\newscrawler\techcrunch.json", encoding="utf-8") as f:
    techcrunch = json.load(f)

# Chuẩn hóa ngày
for item in techcrunch:
    item["date"] = normalize_date_techcrunch(item["date"])

# Gộp
all_news = vnexpress + baoxaydung + techcrunch  

for item in all_news:
    for field in ["title", "author", "content"]:
        if field in item and item[field]:
            item[field] = unescape(item[field])

# Sắp xếp theo ngày
all_news.sort(
    key=lambda x: datetime.strptime(
        x["date"],
        "%Y-%m-%d %H:%M:%S"
    ),
    reverse=True
)

# Xuất file cuối
with open(
    r"C:\Users\Huong Giang\Downloads\newscrawler\newscrawler\tech_news.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        all_news,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"Total articles: {len(all_news)}")