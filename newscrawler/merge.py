import json
import re
from datetime import datetime


def normalize_date(date_str):

    match = re.search(
        r'(\d{1,2})/(\d{1,2})/(\d{4}),\s*(\d{1,2}:\d{2})',
        date_str
    )

    if match:
        day, month, year, hour = match.groups()
        return f"{int(day):02d}/{int(month):02d}/{year}, {hour}"

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

# Gộp
all_news = vnexpress + baoxaydung

# Sắp xếp theo ngày
all_news.sort(
    key=lambda x: datetime.strptime(
        x["date"],
        "%d/%m/%Y, %H:%M"
    ),
    reverse=True
)
# Xuất file cuối
with open(
    "traffic_accidents.json",
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