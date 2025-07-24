
import re
from datetime import datetime

# ファイル読み込み
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 最新日付の取得
latest_date = "2025/4/22"  # ※必要に応じて自動取得に変更可

# 正規表現で「データ更新日：xxxx/x/x」部分を置換
new_html, count = re.subn(r'(データ更新日：)\d{4}/\d{1,2}/\d{1,2}', r'\g<1>' + latest_date, html)

if count == 0:
    print("⚠️ 日付の置換ができませんでした。既存形式と異なる可能性があります。")
else:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"✅ データ更新日を {latest_date} に更新しました")
