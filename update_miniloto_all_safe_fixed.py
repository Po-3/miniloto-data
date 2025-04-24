
import json
from datetime import datetime

HTML_PATH = "index.html"
JSON_PATH = "miniloto_data_for_web_with_features.json"

def parse_date(d):
    try:
        return datetime.strptime(d, "%Y/%m/%d")
    except:
        try:
            return datetime.strptime(d, "%Y/%-m/%-d")  # Unix-like systems
        except:
            return datetime.strptime(d, "%Y/%m/%d")  # fallback

def get_latest_date():
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    dates = [row["日付"] for row in data if "日付" in row and row["日付"]]
    latest_date = max(dates, key=lambda d: datetime.strptime(d, "%Y/%m/%d"))
    return latest_date

def update_html_date(latest_date):
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    updated = False
    if "データ更新日：読み込み中..." in html:
        html = html.replace("データ更新日：読み込み中...", f"データ更新日：{latest_date} ｜ツールVer：1.03")
        updated = True
    else:
        # 既にある更新日を上書きする場合
        import re
        html, count = re.subn(r"データ更新日：[\d/]+", f"データ更新日：{latest_date}", html)
        updated = count > 0

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    if updated:
        print(f"🗓 index.html のデータ更新日を {latest_date} に更新しました")
    else:
        print("⚠️ index.html に更新対象の文字列が見つかりませんでした")

if __name__ == "__main__":
    latest = get_latest_date()
    update_html_date(latest)
