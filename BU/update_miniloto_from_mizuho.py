
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess
import re

# 作業ディレクトリに移動
os.chdir("/Users/po-san/hatena/miniloto-data")

json_path = "miniloto_data_for_web_with_features.json"
url = "https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html"

def judge_features(numbers):
    features = []
    nums = sorted([int(n) for n in numbers])

    if any(b - a == 1 for a, b in zip(nums, nums[1:])):
        features.append("連番あり")
    odd = sum(1 for n in nums if n % 2 == 1)
    even = 5 - odd
    if odd >= 4:
        features.append("奇数多め")
    if even >= 4:
        features.append("偶数多め")
    last_digits = [n % 10 for n in nums]
    if len(set(last_digits)) < len(last_digits):
        features.append("下一桁かぶり")
    total = sum(nums)
    if total < 60:
        features.append("合計小さめ")
    elif total >= 80:
        features.append("合計大きめ")
    if (odd == 3 and even == 2) or (odd == 2 and even == 3):
        features.append("バランス型")

    return "／".join(features)

def fetch_latest_result():
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    text = soup.get_text()

    match = re.search(r"第(\d+)回.*?(\d{4})年(\d{1,2})月(\d{1,2})日.*?本数字：([\d、]+).*?ボーナス数字：([\d]+)", text)
    if not match:
        print("⚠️ 抽せん結果のデータ形式が見つかりません。")
        return None

    kaisu = match.group(1)
    date = f"{match.group(2)}/{match.group(3)}/{match.group(4)}"
    numbers = match.group(5).split("、")
    bonus = match.group(6)

    return {
        "開催回": kaisu,
        "日付": date,
        "第1数字": numbers[0],
        "第2数字": numbers[1],
        "第3数字": numbers[2],
        "第4数字": numbers[3],
        "第5数字": numbers[4],
        "BONUS数字": bonus,
        "1等口数": "0",
        "2等口数": "0",
        "3等口数": "0",
        "4等口数": "0",
        "1等賞金": "0",
        "2等賞金": "0",
        "3等賞金": "0",
        "4等賞金": "0",
        "EOF": "",
        "特徴": judge_features(numbers)
    }

def update_json_and_push():
    entry = fetch_latest_result()
    if entry is None:
        print("⛔ 最新データが取得できなかったため、更新・pushを中止します。")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if any(d["開催回"] == entry["開催回"] for d in data):
        print(f"⚠️ 第{entry['開催回']}回はすでに登録済みです。")
        return

    data.append(entry)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 第{entry['開催回']}回のデータを追加しました。")

    subprocess.run(["git", "add", json_path])
    subprocess.run(["git", "commit", "-m", f"🔄 第{entry['開催回']}回ミニロト追加（自動取得）"])
    subprocess.run(["git", "push"])
    print("🚀 GitHub に自動反映されました。")

if __name__ == "__main__":
    update_json_and_push()
