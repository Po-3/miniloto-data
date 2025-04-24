
import pandas as pd
import json
from datetime import datetime
import subprocess
import re

# === 設定 ===
folder_path = "/Users/po-san/hatena/miniloto-data"
csv_path = f"{folder_path}/miniloto.csv"
json_path = f"{folder_path}/miniloto.json"
html_path = f"{folder_path}/index.html"

# === 特徴判定関数（全7種） ===
def extract_features(row):
    nums = [int(row[f"第{i}数字"]) for i in range(1, 6)]
    features = []

    if any(b - a == 1 for a, b in zip(nums, nums[1:])):
        features.append("連番")

    odd = sum(n % 2 != 0 for n in nums)
    even = 5 - odd
    if odd >= 4:
        features.append("奇数多め")
    elif even >= 4:
        features.append("偶数多め")
    elif odd == 3 or even == 3:
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

# === 1. CSV読み込み（Shift_JIS対応） ===
df = pd.read_csv(csv_path, encoding="cp932", dtype=str)
df["特徴"] = df.apply(extract_features, axis=1)
df = df.sort_values("開催回")

# === 2. JSON出力 ===
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
print("✅ miniloto.json を更新しました")

# === 3. index.html の更新日を最新に書き換え ===
today = datetime.today().strftime("%Y/%m/%d")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r"データ更新日：\d{4}/\d{2}/\d{2}", f"データ更新日：{today}", html)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"🗓 index.html のデータ更新日を {today} に更新しました")

# === 4. Git操作 ===
subprocess.run(["git", "-C", folder_path, "add", "."], check=True)
subprocess.run(["git", "-C", folder_path, "commit", "-m", f"update miniloto data ({today})"], check=True)
subprocess.run(["git", "-C", folder_path, "push"], check=True)
print("🚀 GitHub に push しました")
