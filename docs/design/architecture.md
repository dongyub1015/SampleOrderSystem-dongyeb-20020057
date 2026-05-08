# 시스템 아키텍처

## 1. 레이어드 아키텍처

```
┌─────────────────────────────────────────┐
│           Controller Layer              │
│  input() 수신, 메뉴 흐름 제어            │
│  main / sample / order / approval       │
│  monitoring / production / release      │
├─────────────────────────────────────────┤
│              View Layer                 │
│  print() 전담 출력                       │
│  console_view (공통) / sample_view      │
│  order_view / monitoring_view           │
│  production_view / release_view         │
├─────────────────────────────────────────┤
│            Service Layer                │
│  SampleService / OrderService           │
│  ProductionService / ReleaseService     │
├─────────────────────────────────────────┤
│          Repository Layer               │
│  JsonDataStore 래핑 CRUD                │
│  SampleRepository / OrderRepository    │
│  ProductionRepository                   │
├─────────────────────────────────────────┤
│             Model Layer                 │
│  Sample / Order / ProductionJob         │
│  OrderStatus (Enum)                     │
└─────────────────────────────────────────┘
```

### 레이어 책임

| 레이어 | 책임 | 금지 |
|--------|------|------|
| Controller | `input()` 수신, 메뉴 흐름 제어, View 호출 | `print()` 직접 호출 |
| View | `print()` 출력 전담 | `input()`, model·controller import |
| Service | 비즈니스 규칙 실행, 트랜잭션 조율 | `print()`, `input()` |
| Repository | JsonDataStore CRUD 래핑, 주문번호 생성 | `print()`, `input()`, service import |
| Model | 엔티티 구조 정의, 상태 열거형 | `print()`, `input()`, 타계층 import |

### 의존 방향

```
controller → service → repository → model
```

- Controller는 Service만 호출하며, Repository를 직접 참조하지 않는다
- View는 Controller가 데이터를 넘겨 호출하며, View는 어떤 레이어도 import하지 않는다
- Model은 어떤 레이어도 참조하지 않는다

---

## 2. 컴포넌트 다이어그램

```
main.py → App().run()
  │
  └── app.py (DI Root)
        │
        ├── MainController
        │     ├── SampleController ──── SampleService ──── SampleRepository
        │     │        └── SampleView
        │     ├── OrderController ───── OrderService ───── OrderRepository
        │     │        └── OrderView
        │     ├── ApprovalController ── OrderService
        │     │        │             └─ ProductionService ─ ProductionRepository
        │     │        └── OrderView (재사용)
        │     ├── MonitoringController ─ OrderService
        │     │        │              └─ SampleService
        │     │        └── MonitoringView
        │     ├── ProductionController ─ ProductionService
        │     │        └── ProductionView
        │     └── ReleaseController ─── ReleaseService ─── OrderRepository
        │              └── ReleaseView               └──── SampleRepository
        └── (저장소 싱글턴 인스턴스 공유)
```

---

## 3. 실행 흐름

```
main.py
  └─ App().run()
       └─ app.py (DI Root)
             └─ 저장소 인스턴스 생성 (SampleRepo, OrderRepo, ProductionRepo)
             └─ 서비스 인스턴스 생성 (저장소 주입)
             └─ 컨트롤러 인스턴스 생성 (서비스 + 뷰 주입)
             └─ MainController.run() 루프 진입
                  └─ 사용자 선택 → 하위 컨트롤러 위임
                  └─ 0 입력 시 종료
```

---

## 4. 디렉토리 구조

```
SampleOrderSystem/
├── main.py
├── app.py                       ← DI Root
├── PRD.md
├── PLAN.md
├── CLAUDE.md
├── docs/
│   └── design/
│       ├── architecture.md      ← 이 문서
│       ├── data-model.md
│       ├── state-machine.md
│       └── ui-flow.md
├── model/
│   ├── __init__.py
│   ├── sample.py
│   ├── order.py
│   └── production_job.py
├── repository/
│   ├── __init__.py
│   ├── sample_repository.py
│   ├── order_repository.py
│   └── production_repository.py
├── service/
│   ├── __init__.py
│   ├── sample_service.py
│   ├── order_service.py
│   ├── production_service.py
│   └── release_service.py
├── controller/
│   ├── __init__.py
│   ├── main_controller.py
│   ├── sample_controller.py
│   ├── order_controller.py
│   ├── approval_controller.py
│   ├── monitoring_controller.py
│   ├── production_controller.py
│   └── release_controller.py
└── view/
    ├── __init__.py
    ├── console_view.py
    ├── sample_view.py
    ├── order_view.py
    ├── monitoring_view.py
    ├── production_view.py
    └── release_view.py
```
