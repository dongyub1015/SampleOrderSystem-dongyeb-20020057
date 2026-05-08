# 시스템 아키텍처

## 1. 레이어드 아키텍처

```
┌─────────────────────────────────────────┐
│              UI Layer                   │
│  main_menu / sample_menu / order_menu   │
│  monitoring_menu / production_menu      │
│  release_menu / console (공통 유틸)      │
├─────────────────────────────────────────┤
│            Service Layer                │
│  SampleService / OrderService           │
│  ProductionService / ReleaseService     │
├─────────────────────────────────────────┤
│          Repository Layer               │
│  SampleRepository / OrderRepository    │
│  ProductionRepository                   │
├─────────────────────────────────────────┤
│            Domain Layer                 │
│  Sample / Order / ProductionJob         │
│  OrderStatus (Enum)                     │
└─────────────────────────────────────────┘
```

### 레이어 책임

| 레이어 | 책임 |
|--------|------|
| UI | 사용자 입력 수신, 화면 출력, 메뉴 흐름 제어 |
| Service | 비즈니스 규칙 실행, 트랜잭션 조율 |
| Repository | 인메모리 데이터 저장·조회·삭제 |
| Domain | 엔티티 구조 정의, 상태 열거형 |

### 의존 방향

```
UI → Service → Repository → Domain
```

- 각 레이어는 바로 아래 레이어만 참조한다
- Domain은 어떤 레이어도 참조하지 않는다

---

## 2. 컴포넌트 다이어그램

```
main.py
  │
  ├── MainMenu
  │     ├── SampleMenu ──────── SampleService ── SampleRepository
  │     ├── OrderMenu ─────────  OrderService ── OrderRepository
  │     │                    └─ ProductionService ── ProductionRepository
  │     ├── MonitoringMenu ─── OrderService
  │     │                   └─ SampleService
  │     ├── ProductionMenu ─── ProductionService
  │     └── ReleaseMenu ─────── ReleaseService ── OrderRepository
  │                                             └─ SampleRepository
  └── (저장소 싱글턴 인스턴스 공유)
```

---

## 3. 실행 흐름

```
main.py
  └─ 저장소 인스턴스 생성 (SampleRepo, OrderRepo, ProductionRepo)
  └─ 서비스 인스턴스 생성 (저장소 주입)
  └─ 메뉴 인스턴스 생성 (서비스 주입)
  └─ MainMenu.run() 루프 진입
       └─ 사용자 선택 → 하위 메뉴 위임
       └─ 0 입력 시 종료
```

---

## 4. 디렉토리 구조

```
SampleOrderSystem/
├── main.py
├── PRD.md
├── PLAN.md
├── docs/
│   └── design/
│       ├── architecture.md      ← 이 문서
│       ├── data-model.md
│       ├── state-machine.md
│       └── ui-flow.md
├── domain/
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
└── ui/
    ├── __init__.py
    ├── console.py
    ├── main_menu.py
    ├── sample_menu.py
    ├── order_menu.py
    ├── monitoring_menu.py
    ├── production_menu.py
    └── release_menu.py
```
