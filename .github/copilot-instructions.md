# 聯合通商 GitHub Copilot 規範指引
# ⚠️ 此檔案由 generate_copilot_instructions.py 自動產生
# ⚠️ 請勿手動編輯，修改請直接改 RULES.md
# 最後更新：2025-04-15

你是聯合通商的 AI 開發助理。
產生所有 C# 程式碼時，嚴格遵守以下規範，不得有任何例外。

---

## 🚫 絕對禁止（以下任何一條都不能出現在你產生的程式碼中）

### H001：禁止 hardcode 密碼、API Key、任何憑證
- ❌ 禁止string pwd = "P@ssword1"
- ✅ 必須_config["Auth:Password"]

### H002：禁止 SQL 字串拼接（防 SQL Injection）
- ❌ 禁止"SELECT * WHERE id=" + id
- ✅ 必須cmd.Parameters.Add("@id", id)

### H003：禁止空的 catch block
- ❌ 禁止catch { } 或 catch { // TODO }
- ✅ 必須catch (Exception ex) { _logger.LogError(ex, "說明"); }

### H004：禁止直接 push main branch
- ❌ 禁止：直接 commit 到 main / master
- ✅ 必須：開 feature branch，走 PR 流程

### H005：禁止明文記錄個資到 Log
- ❌ 禁止_logger.Log("身分證：" + idNo)
- ✅ 必須：遮罩處理或不記錄

### H006：禁止忽略 async/await
- ❌ 禁止task.Result 或 task.Wait()
- ✅ 必須await task

### H007：禁止迴圈內直接執行 DB 查詢
- ❌ 禁止foreach(o) { db.Find(o.Id) }
- ✅ 必須：一次批次查詢後再迭代

---

## ⚠️ 強烈建議（除非有特殊理由，否則必須遵守）

### S001：Controller 不直接注入 Repository
- ❌ 避免OrderRepo _repo 在 Controller 建構子
- ✅ 應該：注入 IOrderService

### S002：單一方法不超過 80 行
- ❌ 避免：200 行的 ProcessOrder()
- ✅ 應該：拆成多個職責單一的方法

### S005：非同步方法加 Async 後綴
- ❌ 避免Task GetOrder()
- ✅ 應該Task GetOrderAsync()

### S007：不使用 magic number
- ❌ 避免if (status == 3)
- ✅ 應該if (status == OrderStatus.Cancelled)

---

## 📌 其他固定規範

- 所有 public 方法必須有 /// <summary> XML 文件註解
- 非同步方法名稱結尾必須加 Async
- catch block 必須有 _logger.LogError(ex, "說明") 不可為空
- 所有 Use Case 回傳 Result<T>，業務失敗用 Result.Fail()，不 throw Exception
- 回傳值統一使用 Result<T> 或 IActionResult 包裝

---

## 🏗️ 架構規範

- Controller 只能注入 Service Interface，不能直接注入 Repository
- 模組間只能透過 Interface 溝通，禁止直接 new 另一個模組的類別
- Domain 層禁止 import 任何 Infrastructure 命名空間
- Use Case 類別只有一個 public Execute/Handle 方法

當你不確定某個寫法是否符合規範，請參考 RULES.md 或詢問開發者確認後再產生程式碼。
