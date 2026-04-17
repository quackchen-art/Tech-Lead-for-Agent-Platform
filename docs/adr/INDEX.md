# ADR 索引
# 每次新增 ADR 後更新這個檔案
# ADR 一旦建立不可修改，要改就寫新的 ADR 取代

---

## 使用方式

遇到不確定的架構決策時，搜尋關鍵字欄位，
找到 ADR 編號後執行 `@docs/adr/ADR-00X-xxx.md` 讀取。

---

## 索引表

| 編號 | 標題 | 關鍵字 | 狀態 | 日期 |
|------|------|--------|------|------|
| ADR-001 | 採用模組化單體架構 | 架構、微服務、模組、部署、Monolith、邊界 | ✅ 有效 | 2025-04-15 |
| ADR-002 | Result Pattern 統一回傳格式 | 錯誤處理、Exception、回傳值、Result、失敗、業務 | ✅ 有效 | 2025-04-15 |

---

## 狀態說明

- ✅ 有效：目前採用，開發時遵守
- ⚠️ 已取代：被新 ADR 取代，讀新的
- ❌ 已廢棄：決定不採用或已過時

---

## 新增 ADR 流程

1. 複製 `ADR-000-template.md`，命名為 `ADR-00X-標題.md`
2. 填寫背景、決策、後果
3. 在本 INDEX.md 加一行
4. 把核心結論更新到 `docs/architecture.md`
5. 如有新禁止事項 → 更新 `CLAUDE.md` 和 `RULES.md`
6. 執行 `python scripts/generate_copilot_instructions.py`
