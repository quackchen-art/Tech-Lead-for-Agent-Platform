"""
generate_copilot_instructions.py
從 RULES.md 自動產生 .github/copilot-instructions.md

用途：
  確保 copilot-instructions.md 永遠和 RULES.md 同步
  修改 RULES.md 後執行此腳本即可，不需手動更新兩個檔案

使用方式：
  python scripts/generate_copilot_instructions.py
"""

import re, os
from datetime import datetime

RULES_MD_PATH = "RULES.md"
OUTPUT_PATH   = ".github/copilot-instructions.md"


def parse_rules_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    hard_rules, soft_rules, suggestions = [], [], []

    hard_section = re.search(r'##\s*🚫\s*HARD RULE.*?\n(.*?)(?=##|\Z)', content, re.DOTALL)
    if hard_section:
        for row in re.findall(r'\|\s*(H\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', hard_section.group(1)):
            if row[0].startswith("H"):
                hard_rules.append({"id": row[0], "name": row[1].strip(), "wrong": row[2].strip(), "right": row[3].strip()})

    soft_section = re.search(r'##\s*⚠️\s*SOFT RULE.*?\n(.*?)(?=##|\Z)', content, re.DOTALL)
    if soft_section:
        for row in re.findall(r'\|\s*(S\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', soft_section.group(1)):
            if row[0].startswith("S"):
                soft_rules.append({"id": row[0], "name": row[1].strip(), "wrong": row[2].strip(), "right": row[3].strip()})

    sug_section = re.search(r'##\s*💡\s*SUGGESTION.*?\n(.*?)(?=##|\Z)', content, re.DOTALL)
    if sug_section:
        suggestions = [item.strip() for item in re.findall(r'-\s*(G\d+[：:].+)', sug_section.group(1))]

    return {"hard": hard_rules, "soft": soft_rules, "suggestion": suggestions}


def generate(rules):
    lines = [
        "# 聯合通商 GitHub Copilot 規範指引",
        "# ⚠️ 此檔案由 generate_copilot_instructions.py 自動產生",
        "# ⚠️ 請勿手動編輯，修改請直接改 RULES.md",
        f"# 最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "你是聯合通商的 AI 開發助理。",
        "產生所有 C# 程式碼時，**嚴格遵守**以下規範，不得有任何例外。",
        "",
        "## 🚫 絕對禁止（以下任何一條都不能出現在你產生的程式碼中）",
        "",
    ]
    for r in rules["hard"]:
        lines += [f"### {r['id']}：{r['name']}", f"- ❌ 禁止：`{r['wrong']}`", f"- ✅ 必須：`{r['right']}`", ""]

    lines += ["## ⚠️ 強烈建議（除非有特殊理由，否則必須遵守）", ""]
    for r in rules["soft"]:
        lines += [f"### {r['id']}：{r['name']}", f"- ❌ 避免：`{r['wrong']}`", f"- ✅ 應該：`{r['right']}`", ""]

    if rules["suggestion"]:
        lines += ["## 💡 盡量遵守（提升程式碼品質）", ""]
        lines += [f"- {item}" for item in rules["suggestion"]]
        lines.append("")

    lines += [
        "## 📌 其他固定規範",
        "",
        "- 所有 public 方法必須有 `/// <summary>` XML 文件註解",
        "- 非同步方法名稱結尾必須加 `Async`",
        "- catch block 必須有 `_logger.LogError(ex, \"說明\")` 不可為空",
        "- 所有 Use Case 回傳 `Result<T>`，業務失敗用 `Result.Fail()`，不 throw Exception",
        "- 回傳值統一使用 `Result<T>` 或 `IActionResult` 包裝",
        "- Controller 只能注入 Service Interface，不能直接注入 Repository",
        "- 模組間只能透過 Interface 溝通，禁止直接 new 另一個模組的類別",
        "",
        "當你不確定某個寫法是否符合規範，請參考 RULES.md 或詢問開發者確認後再產生程式碼。",
    ]
    return "\n".join(lines)


def main():
    if not os.path.exists(RULES_MD_PATH):
        print(f"❌ 找不到 {RULES_MD_PATH}")
        return

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    print(f"📖 讀取 {RULES_MD_PATH}...")
    rules = parse_rules_md(RULES_MD_PATH)
    print(f"   HARD: {len(rules['hard'])} 條  SOFT: {len(rules['soft'])} 條  SUGGESTION: {len(rules['suggestion'])} 條")

    content = generate(rules)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 完成！{OUTPUT_PATH} 已更新")


if __name__ == "__main__":
    main()
