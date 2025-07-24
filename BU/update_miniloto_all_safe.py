
# 修正版 update_miniloto_all.py（index.html を上書きせず、データ更新日だけを置換）

import json
from datetime import datetime

HTML_PATH = "index.html"
JSON_PATH = "miniloto_data_for_web_with_features.json"

def get_latest_date():
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    latest = sorted([row["日付"] for row in data if row["日付"]])[-1]
    return latest

def update_html_date(latest_date):
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    new_html = html.replace(
        "データ更新日：読み込み中...",
        f"データ更新日：{latest_date} ｜ツールVer：1.03"
    )
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"🗓 index.html のデータ更新日を {latest_date} に更新しました")

if __name__ == "__main__":
    latest = get_latest_date()
    update_html_date(latest)
