# 系統架構與設計模式
# 每次新增 ADR 後同步更新核心結論
# 上次更新：2025-04-15

---

## 架構總覽

本系統採用模組化單體（Modular Monolith）架構。
詳細決策背景見 ADR-001。

```
MyApp.sln
├── Modules/
│   ├── Order/              訂單生命週期管理
│   │   ├── Domain/
│   │   ├── Application/
│   │   ├── Infrastructure/
│   │   └── IOrderModule.cs
│   ├── Payment/            金流處理
│   │   └── IPaymentModule.cs
│   ├── Notification/       通知發送（規劃中）
│   └── Customer/           客戶資料（規劃中）
└── Shared/
    ├── Domain/             共用 Value Objects、Base Classes、Result<T>
    └── Infrastructure/     共用 DB Context、Event Bus
```

---

## 採用的設計模式

### 1. Result Pattern（回傳格式，ADR-002）

所有 Use Case 回傳 `Result<T>`，不使用 Exception 控制業務流程。

```csharp
// 定義
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? ErrorMessage { get; }

    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(string msg) => new(false, default, msg);
}

// 使用
var result = await _cancelOrderUseCase.ExecuteAsync(request);
if (!result.IsSuccess)
    return BadRequest(result.ErrorMessage);
return Ok(result.Value);
```

禁止：在 Use Case 裡 throw Exception 表示業務失敗。

---

### 2. Repository Pattern（資料存取）

所有 DB 操作透過 Repository Interface，
Application 層和 Domain 層不得直接使用 DbContext。

```csharp
// ✅
public class CancelOrderUseCase(IOrderRepository repo) { }

// ❌
public class CancelOrderUseCase(AppDbContext db) { }
```

---

### 3. Domain Event Pattern（跨模組通知）

跨模組副作用透過 Domain Event 發布，不直接呼叫另一個模組。

```csharp
// Order 模組發布
await _eventPublisher.PublishAsync(new OrderCancelledEvent(orderId));

// Notification 模組訂閱（不知道誰發布的）
public class HandleOrderCancelled : IEventHandler<OrderCancelledEvent> { }
```

---

### 4. Strangler Fig Pattern（舊系統遷移）

舊系統不重寫，在旁邊長出新模組。
新功能 → 新架構，舊功能 → 按計畫搬遷，搬完一個刪一個。

---

## 模組依賴關係

```
Order ←── Payment（Payment 依賴 IOrderModule 查詢訂單）
  ↓
Event Bus
  ↓
Notification（被動訂閱 Domain Events）

Customer ← 被 Order、Payment 依賴（查詢客戶資料）
```

規則：依賴只能透過 Interface，不能直接依賴具體實作。

---

## 不採用的方案

| 方案 | 決策 | 原因 |
|------|------|------|
| 微服務 | 不採用 | 團隊規模不足，運維複雜度過高 |
| CQRS | 暫不採用 | 目前複雜度不需要 |
| Event Sourcing | 不採用 | 複雜度太高，ROI 不足 |
