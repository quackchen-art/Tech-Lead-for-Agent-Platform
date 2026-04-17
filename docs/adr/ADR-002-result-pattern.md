# ADR-002：Result Pattern 統一回傳格式

## 狀態
✅ 有效（2025-04-15）

## 背景

Use Case 層的錯誤處理方式不統一：
- 部分方法 throw Exception 表示業務失敗
- 部分方法回傳 null 表示找不到
- Controller 端的錯誤處理邏輯分散、不一致

## 決策

所有 Use Case 的回傳值統一使用 `Result<T>`：

```csharp
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? ErrorMessage { get; }
    public string? ErrorCode { get; }

    private Result(bool success, T? value, string? msg, string? code)
    {
        IsSuccess = success; Value = value;
        ErrorMessage = msg; ErrorCode = code;
    }

    public static Result<T> Ok(T value) =>
        new(true, value, null, null);

    public static Result<T> Fail(string message, string? code = null) =>
        new(false, default, message, code);
}
```

規則：
- Use Case 的業務失敗（找不到、狀態不對）回傳 `Result.Fail()`
- 系統層面的例外（DB 連線失敗）才 throw Exception
- Controller 統一把 `Result.Fail` 轉成對應的 HTTP 狀態碼

## 後果

正面：
- Use Case 的成功/失敗一目了然
- Controller 端的錯誤處理可以統一化
- 可測試性高，測試只需要斷言 IsSuccess 和 ErrorCode

需要接受的：
- 所有新的 Use Case 都要遵守
- 需要一個共用的 Result<T> 類別放在 Shared 層
- 舊的 Service 方法不強制立刻改，按 Baseline 處理
