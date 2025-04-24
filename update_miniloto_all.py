
import requests
import pandas as pd
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import subprocess

folder = "/Users/po-san/hatena/miniloto-data"
csv_path = f"{folder}/miniloto.csv"
json_path = f"{folder}/miniloto.json"
html_path = f"{folder}/index.html"

# 特徴判定関数（空文字や非数値に対応）
def extract_features(row):
    try:
        nums = []
        for i in range(1, 6):
            val = row[f"第{i}数字"]
            if isinstance(val, str) and val.strip().isdigit():
                nums.append(int(val.strip()))
        if len(nums) < 5:
            return "不明"

        features = []
        if any(b - a == 1 for a, b in zip(nums, nums[1:])):
            features.append("連番")
        odd = sum(n % 2 != 0 for n in nums)
        even = 5 - odd
        if odd >= 4:
            features.append("奇数多め")
        elif even >= 4:
            features.append("偶数多め")
        elif odd == 3:
            features.append("バランス型")
        last_digits = [n % 10 for n in nums]
        if len(set(last_digits)) < 5:
            features.append("下一桁かぶり")
        total = sum(nums)
        if total <= 60:
            features.append("合計小さめ")
        elif total >= 100:
            features.append("合計大きめ")
        return "／".join(features)
    except Exception as e:
        return f"判定エラー:{e}"

# 最新結果の取得（前の最新版と同じ構造）
def fetch_latest_result():
    url = "https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html"
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    with open(f"{folder}/miniloto_raw.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    numbers = [tag.text.strip() for tag in soup.select("b.js-lottery-number-pc")]
    bonus = soup.select_one("b.js-lottery-bonus-pc")
    date_tag = soup.select_one("p.js-lottery-date-pc")
    title_tag = soup.select_one("th.section__table-head.section__table-cell--center.js-lottery-issue-pc")

    if not (numbers and bonus and date_tag and title_tag):
        print("❌ 必要な要素が見つかりませんでした")
        return None

    round_match = re.search(r"(\d+)", title_tag.text)
    round_num = round_match.group(1) if round_match else "???"

    return {
        "開催回": round_num,
        "日付": date_tag.text.strip().replace("年", "/").replace("月", "/").replace("日", ""),
        "第1数字": numbers[0],
        "第2数字": numbers[1],
        "第3数字": numbers[2],
        "第4数字": numbers[3],
        "第5数字": numbers[4],
        "BONUS数字": bonus.text.strip(),
        "1等口数": "",
        "2等口数": "",
        "3等口数": "",
        "4等口数": "",
        "1等賞金": "",
        "2等賞金": "",
        "3等賞金": "",
        "4等賞金": "",
        "EOF": "",
    }

# メイン処理
df = pd.read_csv(csv_path, encoding="cp932", dtype=str)
latest = fetch_latest_result()

if latest:
    if latest["開催回"] not in df["開催回"].values:
        df = pd.concat([df, pd.DataFrame([latest])], ignore_index=True)
        print(f"✅ 第{latest['開催回']}回の結果を追加しました")
    else:
        print("✅ すでに最新結果が含まれています")

    df["特徴"] = df.apply(extract_features, axis=1)
    df = df.sort_values("開催回")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    today = datetime.today().strftime("%Y/%m/%d")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = re.sub(r"データ更新日：\d{4}/\d{2}/\d{2}", f"データ更新日：{today}", html)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    subprocess.run(["git", "-C", folder, "add", "."], check=True)
    subprocess.run(["git", "-C", folder, "commit", "-m", f"Auto-update miniloto ({today})"], check=True)
    subprocess.run(["git", "-C", folder, "push"], check=True)
    print("🚀 自動更新・GitHub反映が完了しました")
