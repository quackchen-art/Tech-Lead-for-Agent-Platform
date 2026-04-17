# 聯合通商 程式開發規範
# 參考來源：Microsoft .NET Design Guidelines、OWASP Top 10、Google Engineering Practices
# 版本：v1.0　建立：2025-04-15　維護人：Caspar
# 修改後執行：python scripts/generate_copilot_instructions.py

---

## 🚫 HARD RULE — 絕對禁止，無任何例外

違反以下規則，程式碼將無法 commit，嘗試繞過者自動通報 Caspar。

| 編號 | 規則說明 | 錯誤範例 | 正確範例 |
|------|---------|---------|---------|
| H001 | 禁止 hardcode 密碼、API Key、任何憑證 | `string pwd = "P@ssword1"` | `_config["Auth:Password"]` |
| H002 | 禁止 SQL 字串拼接（防 SQL Injection） | `"SELECT * WHERE id=" + id` | `cmd.Parameters.Add("@id", id)` |
| H003 | 禁止空的 catch block | `catch { }` | `catch (Exception ex) { _logger.LogError(ex, "..."); }` |
| H004 | 禁止直接 push 到 main / master branch | 直接 git push main | 開 feature branch，走 PR |
| H005 | 禁止明文記錄個資到 Log | `_logger.Log("身分證：" + idNo)` | 遮罩處理或不記錄 |
| H006 | 禁止忽略 async/await（造成死鎖） | `task.Result` 或 `task.Wait()` | `await task` |
| H007 | 禁止在迴圈內直接執行 DB 查詢（N+1） | `foreach(o) { db.Find(o.Id) }` | 一次批次查詢後再迭代 |

---

## ⚠️ SOFT RULE — 建議遵守，可申請例外

| 編號 | 規則說明 | 錯誤範例 | 正確範例 |
|------|---------|---------|---------|
| S001 | Controller 不直接注入 Repository | `OrderRepo _repo` 在 Controller | 注入 `IOrderService` |
| S002 | 單一方法不超過 80 行 | 200 行的 `ProcessOrder()` | 拆成多個職責單一的方法 |
| S003 | Commit message 必須含 Ticket 編號 | `fix bug` | `[TASK-123] 修正取消訂單未退款` |
| S004 | 修改既有方法前加說明註解 | 直接改 | `// [2025-04-15 Oliver] 原因：...` |
| S005 | 非同步方法加 Async 後綴 | `Task GetOrder()` | `Task GetOrderAsync()` |
| S006 | Interface 命名以 I 開頭 | `class OrderService` 作介面 | `interface IOrderService` |
| S007 | 不使用 magic number，改用具名常數 | `if (status == 3)` | `if (status == OrderStatus.Cancelled)` |
| S008 | 方法參數不超過 5 個 | `void Create(a,b,c,d,e,f,g)` | 改用 Request DTO 物件 |
| S009 | 對外 API 回傳統一格式 | 直接 `return order` | `return ApiResponse.Ok(order)` |
| S010 | 資源使用完畢後必須釋放 | `new SqlConnection(...)` 未關閉 | `using (var conn = ...)` |

---

## 💡 SUGGESTION — AI 建議，不強制

- G001：變數命名有業務意義，避免 `temp`、`data`、`obj`、`aaa`
- G002：public 方法加 XML 文件註解 `/// <summary>`
- G003：重複超過 3 次的邏輯抽成共用方法
- G004：if 巢狀超過 3 層考慮重構（Early Return 模式）
- G005：字串組合用 `StringBuilder` 或字串插值，避免 `+` 串接
- G006：集合類型優先宣告為 `IEnumerable<T>` 或 `IReadOnlyList<T>`
- G007：避免 `var` 用在型別不明顯的地方
- G008：Exception 要帶有有意義的訊息
- G009：單元測試命名格式：`方法名稱_情境_預期結果`
- G010：避免使用過時（Obsolete）的 API

---

## 📝 例外申請格式

在違規程式碼的上一行加上：

```csharp
// RULE-EXCEPTION: S001
// 原因：此為 2018 年舊系統相容層，無 Service 層，重構排程 TASK-789 Q3 完成
// Ticket：TASK-789
// 申請人：Oliver　日期：2025-04-15
```

申請驗證規則：
- 原因至少 20 字，需具體描述（填「先這樣」自動拒絕）
- 必須有 Ticket 編號
- 核准有效期：90 天，到期前 7 天自動通知重審
- HARD RULE 不接受例外申請

---

## 🔑 例外唯一核准人：Caspar

---

## 📅 規範更新記錄

| 日期 | 版本 | 修改內容 | 修改人 |
|------|------|---------|-------|
| 2025-04-15 | v1.0 | 初版，參考 MS .NET Guidelines + OWASP | Caspar |
