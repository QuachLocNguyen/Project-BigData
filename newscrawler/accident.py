import json
import re

from transformers import pipeline
from tqdm import tqdm

# =====================================
# LOAD NER MODEL
# =====================================

print("Loading NER model...")

ner = pipeline(
    "token-classification",
    model="NlpHUST/ner-vietnamese-electra-base",
    aggregation_strategy="simple"
)

print("NER model loaded.")

# =====================================
# VEHICLES
# =====================================

VEHICLES = [
    "xe máy",
    "xe tải",
    "xe khách",
    "ô tô",
    "ôtô",
    "container",
    "xe buýt",
    "xe đầu kéo",
    "xe con",
    "xe bán tải",
    "xe ben",
    "xe cứu thương",
    "tàu hỏa",
    "tàu lửa"
]

# =====================================
# VIETNAMESE NUMBERS
# =====================================

VI_NUMBERS = {
    "một": 1,
    "hai": 2,
    "ba": 3,
    "bốn": 4,
    "năm": 5,
    "sáu": 6,
    "bảy": 7,
    "tám": 8,
    "chín": 9,
    "mười": 10
}

# =====================================
# CAUSES
# =====================================

CAUSE_PATTERNS = {

    "driver_fatigue": [
        "ngủ gật",
        "buồn ngủ",
        "thiếu ngủ"
    ],

    "loss_of_control": [
        "mất lái",
        "không làm chủ tay lái",
        "không làm chủ phương tiện",
        "không kiểm soát được xe"
    ],

    "speeding": [
        "quá tốc độ",
        "phóng nhanh",
        "chạy nhanh",
        "không làm chủ tốc độ"
    ],

    "wrong_lane": [
        "đi sai làn",
        "lấn làn",
        "ngược chiều",
        "sang làn đường ngược chiều"
    ],

    "unsafe_overtaking": [
        "vượt ẩu",
        "vượt không an toàn"
    ],

    "drunk_driving": [
        "nồng độ cồn",
        "uống rượu bia",
        "say rượu",
        "say xỉn"
    ],

    "tire_blowout": [
        "nổ lốp",
        "bể lốp"
    ],

    "brake_failure": [
        "mất phanh",
        "hỏng phanh"
    ],

    "poor_visibility": [
        "sương mù",
        "tầm nhìn hạn chế",
        "trời tối"
    ],

    "slippery_road": [
        "đường trơn",
        "mặt đường trơn trượt",
        "mưa lớn"
    ]
}

# =====================================
# LOCATION EXTRACTION
# =====================================
def normalize_location(loc):

    loc = loc.strip()

    loc = re.sub(
        r'^(tỉnh|thành phố|huyện|quận|thị xã|xã|phường|thị trấn|bản|TP\.?)\s+',
        '',
        loc,
        flags=re.IGNORECASE
    )

    loc = re.sub(
        r'\s+',
        ' ',
        loc
    )

    return loc.strip()

def extract_locations(text):

    locations = []

    # ==========================
    # NER
    # ==========================

    try:

        entities = ner(text[:4000])

        for ent in entities:

            entity_group = str(
                ent.get(
                    "entity_group",
                    ""
                )
            ).upper()

            word = ent.get(
                "word",
                ""
            )

            if (
                "LOC" in entity_group
                or
                "LOCATION" in entity_group
            ):

                word = word.replace(
                    "_",
                    " "
                ).strip()

                if len(word) > 1:
                    locations.append(word)

    except Exception:
        pass

    # ==========================
    # REGEX FALLBACK
    # ==========================

    LOCATION_PATTERNS = [

        r'tỉnh\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'thành phố\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'huyện\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'quận\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'thị xã\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'xã\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'phường\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'thị trấn\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'bản\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}',

        r'TP\.?\s*[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2}'
    ]

    for pattern in LOCATION_PATTERNS:

        matches = re.findall(
            pattern,
            text
        )

        locations.extend(matches)

    # ==========================
    # CLEAN
    # ==========================

    BAD_WORDS = [
        "kiểm tra",
        "hiện trường",
        "xuất hiện",
        "phối hợp",
        "cơ quan",
        "chuyên môn",
        "ban đầu",
        "điều tra",
        "xác minh",
        "theo",
        "cho biết"
    ]

    location_map = {}

    for loc in locations:

        key = normalize_location(loc)

        if (
            key not in location_map
            or
            len(loc) > len(location_map[key])
        ):
            location_map[key] = loc

    return sorted(location_map.values())

# =====================================
# VEHICLES
# =====================================

def extract_vehicles(text):

    text = text.lower()

    vehicles = []

    for vehicle in VEHICLES:

        if vehicle in text:
            vehicles.append(vehicle)

    return sorted(
        list(set(vehicles))
    )

# =====================================
# NUMBER CONVERTER
# =====================================

def word_to_num(text):

    text = text.lower().strip()

    if text.isdigit():
        return int(text)

    return VI_NUMBERS.get(text, 0)

# =====================================
# VICTIMS
# =====================================

def extract_victims(text):

    text = text.lower()

    dead = 0
    injured = 0
    casualti = 0

    dead_patterns = [

        r'(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(?:người|nạn nhân).*?(?:tử vong|thiệt mạng|chết)',

        r'làm\s+(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(?:người|nạn nhân).*?(?:tử vong|thiệt mạng|chết)',

        r'khiến\s+(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(?:người|nạn nhân).*?(?:tử vong|thiệt mạng|chết)'
    ]

    injured_patterns = [

        r'(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(?:người|nạn nhân).*?(?:bị thương|nhập viện|cấp cứu|nguy kịch)',

        r'làm\s+(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(?:người|nạn nhân).*?(?:bị thương|nhập viện|cấp cứu|nguy kịch)',

        r'khiến\s+(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(?:người|nạn nhân).*?(?:bị thương|nhập viện|cấp cứu|nguy kịch)'
    ]

    for pattern in dead_patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for m in matches:

            dead = max(
                dead,
                word_to_num(m)
            )

    if re.search(
        r'(tài xế|lái xe|người điều khiển).*?(tử vong|thiệt mạng|chết)',
        text
    ):
        dead = max(dead, 1)

    for pattern in injured_patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for m in matches:

            injured = max(
                injured,
                word_to_num(m)
            )

    return {
        "dead": dead,
        "injured": injured
    }

# =====================================
# CAUSES
# =====================================

def extract_causes(text):

    text = text.lower()

    causes = []

    for cause, patterns in CAUSE_PATTERNS.items():

        for pattern in patterns:

            if pattern in text:

                causes.append({
                    "code": cause,
                    "evidence": pattern
                })

                break

    return causes

# =====================================
# LOAD DATA
# =====================================

print("Loading JSON...")

with open(
    r"C:\Users\Huong Giang\Downloads\newscrawler\traffic_accidents.json",
    "r",
    encoding="utf-8"
) as f:

    articles = json.load(f)

print(f"Loaded {len(articles)} articles")

# =====================================
# BUILD SCHEMA
# =====================================

results = []

for article in tqdm(articles):

    content = article.get(
        "content",
        ""
    )

    result = {

        "accidents": {

            "title": article.get(
                "title",
                ""
            ),

            "date": article.get(
                "date",
                ""
            ),

            "vehicles": extract_vehicles(
                content
            ),

            "victims": extract_victims(
                content
            )
        },

        "sources": {

            "author": article.get(
                "author",
                ""
            ),

            "url": article.get(
                "url",
                ""
            )
        },

        "locations": extract_locations(
            content
        ),

        "causes": extract_causes(
            content
        )
    }

    results.append(result)

# =====================================
# SAVE
# =====================================

output_file = r"C:\Users\Huong Giang\Downloads\newscrawler\accident_schema.json"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=4
    )

print(f"\nSaved {len(results)} records")
print(f"Output: {output_file}")