
import json

def judge_features(numbers):
    features = []
    numbers = [int(n) for n in numbers]
    sorted_nums = sorted(numbers)

    # 連番あり（隣接ペアがあるか）
    if any(b - a == 1 for a, b in zip(sorted_nums, sorted_nums[1:])):
        features.append("連番あり")

    # 奇数・偶数
    odds = sum(1 for n in numbers if n % 2 == 1)
    evens = 5 - odds
    if odds >= 4:
        features.append("奇数多め")
    elif evens >= 4:
        features.append("偶数多め")
    else:
        features.append("バランス型")

    # 下一桁かぶり（下1桁が重複している）
    last_digits = [n % 10 for n in numbers]
    if len(set(last_digits)) < 5:
        features.append("下一桁かぶり")

    # 合計値（小さめ or 大きめ）
    total = sum(numbers)
    if total < 60:
        features.append("合計小さめ")
    elif total >= 80:
        features.append("合計大きめ")

    return "／".join(features)

def update_features(json_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for entry in data:
        if not entry.get("特徴"):
            nums = [entry[f"第{i}数字"] for i in range(1, 6)]
            entry["特徴"] = judge_features(nums)
            updated += 1

    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 特徴を付与した回数：{updated}件")
    print(f"📝 保存完了 → {json_path}")

if __name__ == "__main__":
    update_features("miniloto_data_for_web_with_features.json")
