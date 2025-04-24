
import os
import json
import requests
import subprocess
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

folder = "/Users/po-san/hatena/miniloto-data"
csv_path = os.path.join(folder, "miniloto.csv")
json_path = os.path.join(folder, "miniloto_data_for_web_with_features.json")
html_path = os.path.join(folder, "index.html")
mizuhobank_url = "https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html"

def detect_encoding(file_path):
    import chardet
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]

def extract_features(row):
    nums = [int(row[f"第{i}数字"]) for i in range(1, 6)]
    bonus = int(row["BONUS数字"])
    all_nums = nums + [bonus]

    features = []

    # 連番
    if any(nums[i] + 1 == nums[i + 1] for i in range(len(nums) - 1)):
        features.append("連番")

    # 奇数・偶数
    odd = sum(1 for n in nums if int(n) % 2 == 1)
    even = 5 - odd
    if odd >= 4:
        features.append("奇数多め")
    elif even >= 4:
        features.append("偶数多め")
    else:
        features.append("バランス型")

    # 下一桁かぶり
    last_digits = [n % 10 for n in nums]
    if len(set(last_digits)) < len(last_digits):
        features.append("下一桁かぶり")

    # 合計小さめ・大きめ
    total = sum(nums)
    if total < 75:
        features.append("合計小さめ")
    elif total > 110:
        features.append("合計大きめ")

    return "／".join(features)

def fetch_latest_result():
    res = requests.get(mizuhobank_url)
    soup = BeautifulSoup(res.content, "html.parser")

    try:
        table = soup.find("table", class_="typeTK")
        rows = table.find_all("tr")[1:2]
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 16:
                return None
            return {
                "開催回": cells[0].text.strip().replace("回", ""),
                "日付": cells[1].text.strip().replace("年", "/").replace("月", "/").replace("日", ""),
                "第1数字": cells[2].text.strip(),
                "第2数字": cells[3].text.strip(),
                "第3数字": cells[4].text.strip(),
                "第4数字": cells[5].text.strip(),
                "第5数字": cells[6].text.strip(),
                "BONUS数字": cells[7].text.strip(),
                "1等口数": cells[8].text.strip(),
                "2等口数": cells[9].text.strip(),
                "3等口数": cells[10].text.strip(),
                "4等口数": cells[11].text.strip(),
                "1等賞金": cells[12].text.strip().replace(",", ""),
                "2等賞金": cells[13].text.strip().replace(",", ""),
                "3等賞金": cells[14].text.strip().replace(",", ""),
                "4等賞金": cells[15].text.strip().replace(",", ""),
                "EOF": "",
            }
    except Exception:
        return None

# ファイルエンコーディング自動判定で読み込み
encoding = detect_encoding(csv_path)
df = pd.read_csv(csv_path, encoding=encoding, dtype=str)

# 特徴抽出を再実行
df["特徴"] = df.apply(extract_features, axis=1)

# JSONへ保存
df.to_json(json_path, orient="records", force_ascii=False, indent=2)

# 最新の抽選結果を取得し、既存に含まれていなければ追加
latest_result = fetch_latest_result()
if latest_result and latest_result["開催回"] not in df["開催回"].values:
    new_row = pd.DataFrame([latest_result])
    new_row["特徴"] = new_row.apply(extract_features, axis=1)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)
    print(f"✅ 第{latest_result['開催回']}回の結果を追加しました")
else:
    print("⚠️ 有効な最新データが取得できなかったため追加しませんでした")

# EOFのNaN除去（安全整形）
df["EOF"] = df["EOF"].fillna("")
df.to_json(json_path, orient="records", force_ascii=False, indent=2)

# HTMLの更新日も置換
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    today = datetime.now().strftime("%Y/%m/%d")
    updated_html = html.replace(
        "データ更新日：読み込み中...",
        f"データ更新日：{today} ｜ツールVer：1.01"
    )
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(updated_html)
    print(f"🗓 index.html のデータ更新日を {today} に更新しました")

# Gitに自動コミット＆Push
subprocess.run(["git", "-C", folder, "add", "."], check=True)
subprocess.run(["git", "-C", folder, "commit", "-m", f"Auto-update miniloto ({datetime.now().strftime('%Y/%m/%d')})"], check=True)
subprocess.run(["git", "-C", folder, "push"], check=True)
print("🚀 自動更新・GitHub反映が完了しました")
