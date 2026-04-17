# 聯合通商訂單系統 — AI 開發完整指引
# 版本：v2.0　建立：2025-04-15　維護人：Caspar
# 修改本文件後執行：python scripts/generate_copilot_instructions.py

---

## 啟動指令

輸入 `/init` 時，依序執行：
1. 讀取本文件
2. 讀取 `@docs/activeContext.md`
3. 讀取 `@docs/architecture.md`
4. 回報：目前 Sprint 目標 / 已知架構決策 / 待處理事項

任務涉及特定架構問題時，查詢 `@docs/adr/INDEX.md` 找相關 ADR。

---

## 第一部分：AI 行為準則（Karpathy 四原則）

### 1. Think Before Coding
動手前先思考，不要默默假設。

- 開始實作前，明確說出你的假設
- 如果一個需求有多種解讀，先列出來讓我確認，不要自己選一個
- 如果有更簡單的做法，說出來，哪怕這表示推翻我的想法
- 遇到不清楚的地方，停下來問，不要猜測後繼續

### 2. Simplicity First
最少的程式碼解決問題，不做沒被要求的東西。

- 不新增沒被要求的功能或設定項
- 不為一次性使用的程式碼建立抽象層
- 不加「以後可能用到」的彈性設計
- 寫了 200 行但 50 行能搞定？重寫
- 問自己：資深工程師會說這太複雜嗎？如果會，就簡化

### 3. Surgical Changes
只動必須動的地方，不改自己沒弄壞的東西。

- 不「順手改進」相鄰的程式碼、註解或格式
- 不重構沒壞的東西
- 符合既有程式碼風格，就算你有不同意見
- 發現不相關的死程式碼：提出來，但不要自己刪
- 你的每一行改動都要能直接對應到需求

### 4. Goal-Driven Execution
定義成功標準，不要等我每步指示。

把任務轉成可驗證的目標：
- 「修 bug」→「先寫出重現 bug 的測試，讓它通過」
- 「加功能」→「先定義 AC（Acceptance Criteria），再動手」
- 「重構 X」→「確保測試在重構前後都通過」

多步驟任務先說計畫：
```
1. [步驟] → 驗證：[如何確認完成]
2. [步驟] → 驗證：[如何確認完成]
```

---

## 第二部分：專案資訊

| 項目 | 說明 |
|------|------|
| 系統名稱 | 聯合通商訂單管理系統 |
| 技術棧 | .NET 8 / SQL Server / Visual Studio |
| 架構模式 | 模組化單體（Modular Monolith） |
| 團隊規模 | 5-15 人 |
| 開發工具 | GitHub Copilot + Claude API |
| 規範管控 | RULES.md + check_rules.py + pre-commit |

---

## 第三部分：模組邊界規則（最重要）

### 模組標準結構
```
Modules/{模組名}/
  ├── Domain/           業務實體與規則，完全不依賴任何框架
  │   ├── Entities/
  │   ├── ValueObjects/
  │   └── Events/
  ├── Application/      Use Case，一個 UseCase 只有一個 Execute 方法
  │   ├── UseCases/
  │   └── DTOs/
  ├── Infrastructure/   DB 實作、外部 API 呼叫
  │   ├── Persistence/
  │   └── ExternalServices/
  └── I{模組名}Module.cs   對外唯一公開介面
```

### 現有模組

| 模組 | 職責 | 對外介面 |
|------|------|---------|
| Order | 訂單生命週期、狀態機管理 | IOrderModule |
| Payment | 金流串接、退款處理 | IPaymentModule |
| Notification | Email / SMS 發送 | INotificationModule |
| Customer | 客戶資料、地址管理 | ICustomerModule |

### 允許的跨模組溝通
```csharp
// ✅ 透過 Interface 呼叫
var order = await _orderModule.GetOrderAsync(orderId);

// ✅ 透過 Domain Event（非同步）
await _eventPublisher.PublishAsync(new OrderCancelledEvent(orderId));
```

### 絕對禁止
```csharp
// ❌ 禁止跨模組直接 new 具體實作
var svc = new OrderService();

// ❌ 禁止跨模組直接查 DB
var order = await _dbContext.Orders.FindAsync(id); // 在 Payment 模組裡

// ❌ 禁止 Controller 寫業務邏輯
order.Status = "Cancelled"; await _db.SaveChangesAsync(); // 在 Controller 裡

// ❌ 禁止 Domain 層 import Infrastructure
using Microsoft.EntityFrameworkCore; // 在 Domain 層裡
```

---

## 第四部分：命名規範

| 類型 | 格式 | 範例 |
|------|------|------|
| Use Case | 動詞 + 名詞 + UseCase | CancelOrderUseCase |
| Domain Event | 名詞 + 過去式 + Event | OrderCancelledEvent |
| Repository Interface | I + 名詞 + Repository | IOrderRepository |
| 模組對外介面 | I + 模組名 + Module | IOrderModule |
| 非同步方法 | 方法名 + Async | GetOrderAsync |
| DTO | 動作 + 名詞 + Request/Response | CancelOrderRequest |

---

## 第五部分：技術模式規範

### Result Pattern（統一回傳格式，ADR-002）
```csharp
// ✅ 所有 Use Case 回傳 Result<T>
public async Task<Result<OrderDto>> CancelOrderAsync(int id)
{
    if (order == null) return Result<OrderDto>.Fail("訂單不存在");
    return Result<OrderDto>.Ok(dto);
}

// ❌ 禁止用 Exception 控制業務流程
throw new OrderNotFoundException(); // 業務失敗不用 Exception
```

### 錯誤處理
```csharp
// ✅ catch 必須有 log
catch (Exception ex)
{
    _logger.LogError(ex, "取消訂單失敗，OrderId: {OrderId}", orderId);
    return Result<OrderDto>.Fail("系統錯誤");
}

// ❌ 禁止空 catch
catch { }
```

---

## 第六部分：開發規範摘要

完整規則見 `RULES.md`，關鍵項目：

**HARD RULE — 無例外，commit 前直接擋：**
- H001：禁止 hardcode 密碼、API Key、連線字串
- H002：禁止 SQL 字串拼接，必須用參數化查詢或 ORM
- H003：禁止空的 catch block
- H004：禁止直接 push 到 main / master branch
- H005：禁止明文記錄個資到 Log
- H006：禁止 task.Result / task.Wait()（造成死鎖）
- H007：禁止在迴圈內直接執行 DB 查詢（N+1）

**SOFT RULE — 可申請例外，需 Caspar 核准：**
- S001：Controller 不直接注入 Repository
- S002：單一方法不超過 80 行
- S003：Commit message 必須含 Ticket 編號
- S004：修改既有方法前加說明註解
- S005：非同步方法加 Async 後綴
- S006：Interface 命名以 I 開頭
- S007：不使用 magic number，改用具名常數
- S008：方法參數不超過 5 個
- S009：對外 API 回傳統一格式
- S010：資源使用後必須釋放（using）

**例外申請格式：**
```csharp
// RULE-EXCEPTION: S001
// 原因：此為舊系統相容層，重構計畫 TASK-334，Q3 完成
// Ticket：TASK-334
// 申請人：Oliver　日期：2025-04-15
```
唯一核准人：Caspar

---

## 第七部分：既有技術債（Baseline）

以下違規已登記在 `.baseline.json`，不干擾現有開發，但不得新增同類問題：

| 檔案 | 違規 | 重構計畫 |
|------|------|---------|
| LegacyOrderController.cs | S001 直接呼叫 Repository | Q3，TASK-334 |
| OldReportService.cs | S002 業務邏輯混入 DB 查詢 | Q4 |

---

## 第八部分：Strangler Fig 導入原則

1. 新功能一律寫在 `Modules/` 下，用新架構
2. 修改舊程式：只改必須改的，不順手重構
3. 舊程式遷移：按季度計畫執行
4. 新程式碼不可依賴舊程式碼的壞習慣

---

## 第九部分：ADR 查詢

遇到架構疑問時，先查 `@docs/adr/INDEX.md` 的關鍵字欄位。
找到編號後執行 `@docs/adr/ADR-00X.md` 讀取。
不要自己發明已經決定過的東西。

---

_這份文件是 AI 開發的最高指引。有衝突時以本文件為準。_
