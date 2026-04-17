# ADR-001：採用模組化單體架構

## 狀態
✅ 有效（2025-04-15）

## 背景

聯合通商現有系統為傳統分層架構（Controller → Service → Repository）。
隨著功能增加，Service 層出現「神 Service」現象，技術債持續累積。
評估以下三個選項：微服務、模組化單體、直接上 Clean Architecture。

## 決策

採用模組化單體（Modular Monolith）。

選擇模組化單體而非微服務：
- 團隊 5-15 人，不具備微服務運維能力（Service Discovery、分散式追蹤、多 CI/CD）
- 沒有專職 DevOps 人員
- 目前沒有不同服務需要獨立擴展的需求
- 微服務的分散式交易（Saga、2PC）複雜度過高

選擇模組化單體而非直接上 Clean Architecture：
- Clean Architecture 學習曲線高，小團隊初期導入成本過大
- 模組化單體是容器，Clean Architecture 可在模組內逐步實踐
- 兩者不互斥，可以漸進導入

核心邊界規則：
- 每個模組只能透過 Interface（IXxxModule）對外提供功能
- 跨模組副作用一律透過 Domain Event
- 禁止跨模組直接存取 DB

## 後果

正面：
- 部署簡單，不需要額外運維能力
- 模組邊界清晰，各模組可獨立測試
- 日後若有需要，可把單個模組拆成微服務，代價低

需要接受的：
- 嚴格執行模組邊界規則，依賴 check_rules.py 自動掃描
- 舊程式按 Strangler Fig 模式逐步遷移
- 跨模組交易需採用 Outbox Pattern 或 Saga
