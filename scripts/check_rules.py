"""
check_rules.py
聯合通商程式碼規範檢查腳本

使用方式：
  python scripts/check_rules.py                     掃描本次 commit 異動的 .cs 檔案
  python scripts/check_rules.py --all               掃描整個專案
  python scripts/check_rules.py --file xxx.cs       掃描單一檔案
  python scripts/check_rules.py --generate-baseline 產生 Baseline 技術債清單

回傳值：
  0 = 全部通過（或只有 SOFT 警告）
  1 = 有 HARD 違規（擋住 commit）
"""

import re, sys, os, json
from datetime import datetime

RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

RULES = [
    {
        "id": "H001", "level": "HARD",
        "name": "禁止 hardcode 密碼或連線字串",
        "pattern": r'(?i)(password\s*=\s*["\'][^"\']{3,}["\']|connectionstring\s*=\s*["\'][^"\']{5,}["\'])',
        "fix": '改用設定檔：_configuration.GetConnectionString("名稱") 或 _configuration["AppSettings:Key"]',
    },
    {
        "id": "H002", "level": "HARD",
        "name": "禁止 SQL 字串拼接",
        "pattern": r'(?i)(SELECT|INSERT|UPDATE|DELETE).{0,100}["\']\s*\+\s*\w',
        "fix": '改用參數化查詢：cmd.Parameters.AddWithValue("@參數", 值) 或使用 Entity Framework',
    },
    {
        "id": "H003", "level": "HARD",
        "name": "禁止空的 catch block",
        "pattern": r'catch\s*(\([^)]*\))?\s*\{\s*(//[^\n]*)?\s*\}',
        "fix": '在 catch 裡加上：_logger.LogError(ex, "說明發生什麼事");',
    },
    {
        "id": "H006", "level": "HARD",
        "name": "禁止 task.Result / task.Wait() 造成死鎖",
        "pattern": r'\btask\.(Result|Wait)\b|\.\bResult\b\s*;',
        "fix": '改用 await：var result = await task;',
    },
    {
        "id": "H007", "level": "HARD",
        "name": "禁止在迴圈內直接執行 DB 查詢（N+1）",
        "pattern": r'(for|foreach|while)\s*\([^)]*\)\s*\{[^}]*(\.Find|\.FindAsync|\.FirstOrDefault|\.Where\()',
        "fix": '改為一次批次查詢後再迭代，例如先 var ids = orders.Select(o => o.Id).ToList()，再一次查詢',
    },
    {
        "id": "S001", "level": "SOFT",
        "name": "Controller 不應直接注入 Repository",
        "pattern": r'class\s+\w+Controller[^{]*{[^}]*\(\s*[^)]*Repository[^)]*\)',
        "fix": "改為注入對應的 IXxxService，業務邏輯放在 Service 層",
    },
    {
        "id": "S005", "level": "SOFT",
        "name": "非同步方法名稱必須加 Async 後綴",
        "pattern": r'(public|private|protected)\s+(async\s+)?Task(<[^>]*>)?\s+(?!.*Async\s*\()(\w+(?<!Async))\s*\(',
        "fix": "在方法名稱後面加上 Async，例如：GetOrder → GetOrderAsync",
    },
    {
        "id": "S007", "level": "SOFT",
        "name": "避免使用 magic number",
        "pattern": r'(?<!\w)(if|while|==|!=|>|<|>=|<=)\s*\d{2,}\b(?!\s*\.\s*\d)',
        "fix": "改用具名常數，例如：const int MAX_RETRY = 3",
    },
    {
        "id": "G001", "level": "SUGGESTION",
        "name": "避免使用無意義變數名稱",
        "pattern": r'\bvar\s+(temp|data|obj|aaa|bbb|xxx|test)\s*=',
        "fix": "改用描述業務意義的名稱，例如：var tempData → var cancelledOrders",
    },
]

EXCEPTION_PATTERN = r'//\s*RULE-EXCEPTION:\s*(\w+)'


def scan_file(filepath):
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, "r", encoding="cp950") as f:
            lines = f.readlines()

    full_content = "".join(lines)

    for rule in RULES:
        for match in re.finditer(rule["pattern"], full_content, re.MULTILINE | re.DOTALL):
            line_number = full_content[:match.start()].count("\n") + 1
            code_line = lines[line_number - 1].strip() if line_number <= len(lines) else ""

            has_exception = False
            for check_line in lines[max(0, line_number - 4):line_number - 1]:
                m = re.search(EXCEPTION_PATTERN, check_line)
                if m and m.group(1) == rule["id"]:
                    has_exception = True
                    break

            violations.append({
                "file": filepath, "line": line_number,
                "rule_id": rule["id"], "level": rule["level"],
                "name": rule["name"], "fix": rule.get("fix", ""),
                "code": code_line[:120], "has_exception": has_exception,
            })

    return violations


def get_changed_files():
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".cs") and f]


def load_baseline():
    if not os.path.exists(".baseline.json"):
        return set()
    with open(".baseline.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return {f"{v['file']}:{v['line']}:{v['rule_id']}" for v in data.get("violations", [])}


def print_violation(v, is_new):
    if v["has_exception"]:
        color, icon, tag = BLUE, "📋", "待審例外"
    elif v["level"] == "HARD":
        color, icon, tag = RED, "🚫", "HARD RULE"
    elif v["level"] == "SOFT":
        color, icon, tag = YELLOW, "⚠️ ", "SOFT RULE"
    else:
        color, icon, tag = BLUE, "💡", "SUGGESTION"

    old_tag = "" if is_new else "  [既有技術債，已豁免]"
    print(f"\n{color}{BOLD}{icon} {tag}: {v['rule_id']} — {v['name']}{RESET}{old_tag}")
    print(f"   位置：{v['file']}:{v['line']}")
    print(f"   程式碼：{v['code']}")
    if not v["has_exception"] and v["fix"]:
        print(f"   {GREEN}建議修法：{v['fix']}{RESET}")
    if v["has_exception"]:
        print(f"   {BLUE}已申請例外，等待 Caspar 核准{RESET}")
    if v["level"] == "SOFT" and not v["has_exception"] and is_new:
        print(f"   {YELLOW}申請例外方式，在上一行加上：{RESET}")
        print(f"   // RULE-EXCEPTION: {v['rule_id']}")
        print(f"   // 原因：（請填寫至少 20 字的具體原因）")
        print(f"   // Ticket：TASK-xxx")
        print(f"   // 申請人：你的名字　日期：{datetime.now().strftime('%Y-%m-%d')}")


def main():
    if "--generate-baseline" in sys.argv:
        generate_baseline()
        return

    print(f"\n{BOLD}{'─'*52}")
    print("  聯合通商規範檢查")
    print(f"{'─'*52}{RESET}\n")

    if "--all" in sys.argv:
        files = collect_all_cs_files()
        print(f"掃描模式：全專案（共 {len(files)} 個 .cs 檔案）\n")
    elif "--file" in sys.argv:
        idx = sys.argv.index("--file") + 1
        files = [sys.argv[idx]]
        print(f"掃描模式：單一檔案 {files[0]}\n")
    else:
        files = get_changed_files()
        if not files:
            print(f"{GREEN}✅ 沒有 .cs 檔案異動，跳過檢查{RESET}\n")
            sys.exit(0)
        print(f"掃描模式：本次異動（共 {len(files)} 個檔案）\n")

    baseline = load_baseline()
    all_violations = []
    for f in files:
        if os.path.exists(f):
            all_violations.extend(scan_file(f))

    hard_new, soft_new, suggestions, exceptions, baseline_list = [], [], [], [], []

    for v in all_violations:
        key = f"{v['file']}:{v['line']}:{v['rule_id']}"
        is_baseline = key in baseline
        if v["has_exception"]:
            exceptions.append((v, not is_baseline))
        elif is_baseline:
            baseline_list.append(v)
        elif v["level"] == "HARD":
            hard_new.append(v)
        elif v["level"] == "SOFT":
            soft_new.append(v)
        else:
            suggestions.append(v)

    if hard_new:
        print(f"{RED}{BOLD}{'━'*52}")
        print(f"  🚫 HARD RULE 違規（必須修正才能 commit）")
        print(f"{'━'*52}{RESET}")
        for v in hard_new:
            print_violation(v, True)

    if soft_new:
        print(f"\n{YELLOW}{BOLD}{'━'*52}")
        print(f"  ⚠️  SOFT RULE 警告")
        print(f"{'━'*52}{RESET}")
        for v in soft_new:
            print_violation(v, True)

    if exceptions:
        print(f"\n{BLUE}{BOLD}{'━'*52}")
        print(f"  📋 已申請例外（等待 Caspar 核准）")
        print(f"{'━'*52}{RESET}")
        for v, is_new in exceptions:
            print_violation(v, is_new)

    if baseline_list:
        print(f"\n{'─'*52}")
        print(f"  既有技術債（已豁免）：{len(baseline_list)} 筆")

    print(f"\n{'━'*52}")
    if not hard_new:
        print(f"{GREEN}{BOLD}✅ 檢查通過{RESET}")
        if soft_new:
            print(f"{YELLOW}   {len(soft_new)} 個 SOFT 警告，建議處理或申請例外{RESET}")
        if exceptions:
            print(f"{BLUE}   {len(exceptions)} 個例外申請等待 Caspar 核准{RESET}")
        print(f"{'━'*52}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}❌ 發現 {len(hard_new)} 個 HARD RULE 違規，無法 commit{RESET}")
        print(f"   請修正上述問題後再重新提交")
        print(f"{'━'*52}\n")
        sys.exit(1)


def collect_all_cs_files():
    files = []
    for root, dirs, filenames in os.walk("."):
        dirs[:] = [d for d in dirs if d not in [".git", "bin", "obj", "packages", "node_modules"]]
        files.extend(os.path.join(root, f) for f in filenames if f.endswith(".cs"))
    return files


def generate_baseline():
    print("產生 Baseline 技術債清單...\n")
    files = collect_all_cs_files()
    all_violations = []
    for f in files:
        if os.path.exists(f):
            all_violations.extend(scan_file(f))

    data = {
        "generated_at": datetime.now().isoformat(),
        "total_files": len(files),
        "total_violations": len(all_violations),
        "violations": [
            {"file": v["file"], "line": v["line"], "rule_id": v["rule_id"], "level": v["level"], "code": v["code"]}
            for v in all_violations
        ]
    }

    with open(".baseline.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    hard = len([v for v in all_violations if v["level"] == "HARD"])
    soft = len([v for v in all_violations if v["level"] == "SOFT"])
    print(f"✅ Baseline 產生完成：.baseline.json")
    print(f"   掃描檔案：{len(files)} 個")
    print(f"   技術債總計：{len(all_violations)} 筆（HARD: {hard}，SOFT: {soft}）")
    print(f"\n既有違規已登記在案，後續新程式碼才需符合規範。")


if __name__ == "__main__":
    main()
