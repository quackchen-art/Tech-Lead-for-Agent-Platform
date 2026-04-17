# 目前工作上下文
# 每個 Sprint 開始時更新，重大決策發生時隨時補充
# 上次更新：2025-04-15　更新人：Caspar

---

## 目前 Sprint（2025-04-15 ～ 2025-04-28）

### Sprint 目標
建立 AI 輔助開發規範體系，讓開發者馬上可以開始使用。

### 已完成
- [x] RULES.md 初版（7 HARD + 10 SOFT + 10 SUGGESTION）
- [x] CLAUDE.md 完整版（含 Karpathy 四原則 + 架構說明）
- [x] copilot-instructions.md（自動產生）
- [x] check_rules.py 掃描引擎
- [x] generate_copilot_instructions.py 自動同步工具
- [x] pre-commit 設定
- [x] ADR-001（模組化單體架構）
- [x] ADR-002（Result Pattern）
- [x] Memory Bank 結構（docs/）

### 進行中
- [ ] 執行 Baseline 全庫掃描（第一次啟動時執行）
- [ ] 設定 GitHub Actions 每日品質報告
- [ ] 安裝 GitHub Copilot（各開發者）

### 下個 Sprint 預計
- Order 模組第一個 Use Case 重構（CancelOrderUseCase）
- Payment 模組介面定義（IPaymentModule）
- 建立共用 Result<T> 類別

---

## 近期重要決策

| 日期 | 決策 | ADR |
|------|------|-----|
| 2025-04-15 | 採用模組化單體架構 | ADR-001 |
| 2025-04-15 | Result Pattern 統一回傳格式 | ADR-002 |
| 2025-04-15 | 開發規範三級分類（HARD/SOFT/SUGGESTION） | — |
| 2025-04-15 | RULES.md 為規範唯一來源，其他檔案自動產生 | — |

---

## 目前已知風險

1. LegacyOrderController.cs 有大量直接 DB 呼叫，修改時需特別小心
2. OldReportService.cs 邏輯不清楚，建議修改前先閱讀相關測試
3. 開發者 Copilot 尚未安裝，需要 Week 2 完成
