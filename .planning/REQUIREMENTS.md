# Requirements: Граф денег

**Defined:** 2026-09-23
**Core Value:** Аналитик видит кого проверять первым и почему.

## v1 Requirements

### Data and execution

- [x] **DATA-01**: Один локальный запуск обрабатывает edges, nodes, transactions parquet и создаёт все результаты менее чем за 300 секунд.
- [x] **DATA-02**: Все входные gid, включая изолированные seed, сохранены ровно один раз; проверяются ссылки и согласованность сумм/числа транзакций.
- [x] **DATA-03**: Аналитика и UI используют общий документированный версионированный JSON-контракт, gid в браузере строковый.

### Explainable analysis

- [x] **ROLE-01**: Каждый узел имеет одну из шести ролей, role_score и priority_score в [0,1], cluster_id и непустое evidence ≤200 символов.
- [x] **ROLE-02**: Правила, пороги и разрешение пересечений задокументированы; карточка объясняет решение по метрикам для произвольного gid.
- [x] **ROLE-03**: Depth=4 без исходящих не классифицируется terminal из-за обрыва; seed и неполнота входящего потока отмечаются; выводы только гипотезы.
- [x] **CLUS-01**: Каждый узел отнесён к сообществу; clusters.csv содержит cluster_id,n_nodes,n_seed,sum_kzt_internal,top_gids,hypothesis.
- [x] **RANK-01**: top_nodes.csv содержит ≥20 уникальных ранжированных узлов с rank,gid,role,priority_score,why.

### Analyst interface

- [x] **UI-01**: Локальный интерфейс на shadcn/ui показывает направленный граф, роли и кластеры с легендой.
- [x] **UI-02**: Поиск любого gid открывает его карточку и связи, включая граничные узлы и изоляты; топ-лист связан с графом.
- [x] **UI-03**: Аналитик скачивает три CSV фиксированных схем; видит понятные загрузку, ошибку, пустые результаты и ограничения данных.
- [ ] **UI-04**: Интерфейс минималистичен, читаем, доступен клавиатурой и адаптируется к узкому экрану; локальная сборка не зависит от CDN.

### Delivery

- [x] **SHIP-01**: README содержит установку, одну команду расчёта, запуск UI, правила/пороги, ограничения и масштабирование до ~1 млн узлов.
- [x] **SHIP-02**: Есть диаграмма решения и сценарий 5-минутного демо с живым запуском и разбором 2–3 узлов.
- [x] **TEST-01**: Тесты покрывают роли, границу, seed, изоляты, контракты CSV/JSON, воспроизводимость и основной путь UI; полный реальный прогон измерен.

## v2 Requirements

- [x] **TIME-01**: Временные признаки транзита за 1–2 дня и всплесков с оговоркой о невозможности доказать идентичность денег.
- [x] **EXPL-01**: Карточка рекомендует следующий запрос недостающих данных; дополнительные фильтры/обзор кластеров.
- [ ] **AI-01**: Необязательный ассистент отвечает только по вычисленным метрикам со ссылками на gid.

## Out of Scope

| Feature | Reason |
|---|---|
| Хардкод gid, вымышленные клиентские атрибуты | Запрещено кейсом |
| GPU, платные сервисы, облачная инфраструктура | Запрещены как условие воспроизведения |
| Авторизация, потоковая обработка | Не нужны для локального батча |

### Redesign acceptance

- [ ] **UX-01**: Priority → graph → evidence workflow is visible and understandable on the first desktop screen.
- [ ] **UX-02**: Graph identifies incoming/outgoing direction and amounts, has readable node identity/role and explicit dense-neighborhood scope.
- [ ] **UX-03**: Desktop and mobile screenshots plus analyst browser journey independently checked; all original UI functions preserved.

### Optional enhancements in implementation

- [ ] **ROUTE-01**: Enumerate bounded deterministic directed A→B→C paths and 2–3-node return cycles with aggregate leg evidence and string gid references.
- [ ] **ROUTE-02**: Distinguish topology, strictly ordered dates, ambiguous same-day observations and recurrence across distinct episode-start days; disclose that dates cannot trace the same money.
- [ ] **ROUTE-03**: Selected-node UI navigates every cited gid, exposes caps/truncation and unavailable states without altering original exports.
- [ ] **RES-01**: Simulate fixed existing-priority top-N node removal, N=0..cap, on a copy and preserve original graph.
- [ ] **RES-02**: Include isolates and before/after weak-component, largest-component and isolate metrics with both surviving and original denominators.
- [ ] **RES-03**: Bounded UI scenario selector labels hypothetical removal and retains original data/export behavior.
- [ ] **ANOM-01**: Compare observed node metrics within same-depth cohorts using deterministic robust baseline and explicit cohort size.
- [ ] **ANOM-02**: Handle small cohorts, zero MAD, seed and boundary censoring; only characterize transactions observed at/above the 5,000 KZT cutoff.
- [ ] **ANOM-03**: Present explanation, raw metric, peer baseline and limitation in the selected-node UI without risk probabilities.
- [ ] **AI-02**: Real opt-in LLM provider with disabled offline/free baseline and explicit unavailable behavior.
- [ ] **AI-03**: Server-owned bounded allowlisted read-only query tools, validated string gid citations, prompt-injection isolation and honest missing-information answers.
- [ ] **AI-04**: Independent grounded-answer evaluation and baseline regression including all five must-haves, under-300-second batch, and all eight optional case features.

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Complete |
| DATA-02 | Phase 1 | Complete |
| DATA-03 | Phase 1 | Complete |
| ROLE-01 | Phase 1 | Complete |
| ROLE-02 | Phase 1 | Complete |
| ROLE-03 | Phase 1 | Complete |
| CLUS-01 | Phase 1 | Complete |
| RANK-01 | Phase 1 | Complete |
| UI-01 | Phase 1 | Complete |
| UI-02 | Phase 1 | Complete |
| UI-03 | Phase 1 | Complete |
| UI-04 | Phase 3 | Technical checks passed; user visual review open |
| SHIP-01 | Phase 1 | Complete |
| SHIP-02 | Phase 1 | Complete |
| TEST-01 | Phase 1 | Complete |
| TIME-01 | Phase 2 | Complete |
| EXPL-01 | Phase 2 | Complete |
| UX-01 | Phase 3 | Technical checks passed; user visual review open |
| UX-02 | Phase 3 | Technical checks passed; user visual review open |
| UX-03 | Phase 3 | Technical checks passed; user visual review open |
| ROUTE-01 | Phase 4 | In progress |
| ROUTE-02 | Phase 4 | In progress |
| ROUTE-03 | Phase 4 | In progress |
| RES-01 | Phase 5 | In progress |
| RES-02 | Phase 5 | In progress |
| RES-03 | Phase 5 | In progress |
| ANOM-01 | Phase 6 | In progress |
| ANOM-02 | Phase 6 | In progress |
| ANOM-03 | Phase 6 | In progress |
| AI-01 | Phase 7 | In progress |
| AI-02 | Phase 7 | In progress |
| AI-03 | Phase 7 | In progress |
| AI-04 | Phase 7 | In progress |

All 33 requirement IDs map to a single active phase. UI-04 moved from Phase 1 to Phase 3 after the readability rejection. AI-01 is planned in Phase 7; the later user request authorizes its implementation and a real-model verification gate.
