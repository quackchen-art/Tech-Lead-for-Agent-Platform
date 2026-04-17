# 聯合通商 AI 輔助開發規範體系

## 目錄結構

```
專案根目錄/
├── CLAUDE.md                        AI 開發完整指引（自動讀取）
├── RULES.md                         程式開發規範（唯一來源）
├── .baseline.json                   既有技術債清單（第一次執行產生）
├── .pre-commit-config.yaml          Git Hook 設定
│
├── .github/
│   ├── copilot-instructions.md      AI 補程式碼指引（自動產生，勿手動改）
│   └── workflows/
│       └── daily-report.yml         每日品質報告排程
│
├── scripts/
│   ├── check_rules.py               規範掃描引擎
│   └── generate_copilot_instructions.py  自動同步工具
│
└── docs/
    ├── activeContext.md             目前 Sprint 上下文
    ├── architecture.md              系統架構與設計模式
    └── adr/
        ├── INDEX.md                 ADR 索引（每次新增 ADR 更新）
        ├── ADR-000-template.md      新 ADR 複製範本
        ├── ADR-001-modular-monolith.md
        └── ADR-002-result-pattern.md
```

---

## 第一次啟動 SOP

### Step 1：安裝 pre-commit
```bash
pip install pre-commit
pre-commit install
```

### Step 2：產生 Baseline（只執行一次）
```bash
python scripts/check_rules.py --generate-baseline
git add .baseline.json
git commit -m "[INIT] 建立規範 Baseline"
```

### Step 3：同步 AI 指引
```bash
python scripts/generate_copilot_instructions.py
```

### Step 4：安裝 GitHub Copilot
Visual Studio → Extensions → Manage Extensions → 搜尋 GitHub Copilot → Install

### Step 5：設定每日報告 Email（GitHub Secrets）
GitHub 專案 → Settings → Secrets and variables → Actions
- MAIL_USERNAME：你的 Gmail 帳號
- MAIL_PASSWORD：Gmail 應用程式密碼

---

## 日常使用

### 開新對話（Claude Code）
```
輸入：/init
```
AI 自動讀取 CLAUDE.md + activeContext.md + architecture.md

### 需要查架構決策
```
查詢 @docs/adr/INDEX.md 的關鍵字欄位
再執行 @docs/adr/ADR-00X.md 讀取
```

### 修改規範
```
1. 修改 RULES.md
2. 執行：python scripts/generate_copilot_instructions.py
3. commit（pre-commit 會自動同步）
```

### 新增 ADR
```
1. 複製 docs/adr/ADR-000-template.md
2. 填寫內容
3. 更新 docs/adr/INDEX.md
4. 同步核心結論到 docs/architecture.md
5. 若有新禁止事項 → 更新 CLAUDE.md 和 RULES.md
```

---

## 規範三級說明

| 級別 | 說明 | 違規後果 |
|------|------|---------|
| HARD RULE | 涉及安全性或架構破壞 | 直接擋住 commit，無例外 |
| SOFT RULE | 架構規範與程式品質 | 警告，可申請例外（需 Caspar 核准） |
| SUGGESTION | 可讀性與最佳實踐 | AI 提示，不影響 commit |

---

## 例外申請

唯一核准人：Caspar

```csharp
// RULE-EXCEPTION: S001
// 原因：此為舊系統相容層，重構計畫 TASK-334，Q3 完成
// Ticket：TASK-334
// 申請人：Oliver　日期：2025-04-15
```

---

## 常用指令

```bash
# 掃描異動檔案
python scripts/check_rules.py

# 掃描整個專案
python scripts/check_rules.py --all

# 掃描單一檔案
python scripts/check_rules.py --file path/to/file.cs

# 產生 Baseline（只執行一次）
python scripts/check_rules.py --generate-baseline

# 同步 AI 指引
python scripts/generate_copilot_instructions.py
```
