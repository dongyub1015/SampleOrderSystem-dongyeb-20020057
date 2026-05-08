# PLAN: 반도체 시료 생산주문관리 시스템 구현 계획

## 1. 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.10+ |
| 데이터 저장 | JSON 파일 (JsonDataStore — DataPersistence-dongyeb-20020057) |
| 외부 의존성 | DataPersistence-dongyeb-20020057 (`data_store.py`, `exceptions.py`) |
| 실행 방식 | `python main.py` |

---

## 2. 디렉토리 구조

```
SampleOrderSystem/
├── main.py                          # 진입점 (App().run() 한 줄)
├── app.py                           # DI Root: 저장소→서비스→컨트롤러 생성·주입
├── PRD.md
├── PLAN.md
├── CLAUDE.md
├── docs/
│   └── design/
│       ├── architecture.md
│       ├── data-model.md
│       ├── state-machine.md
│       └── ui-flow.md
├── model/
│   ├── __init__.py
│   ├── sample.py                    # Sample 엔티티
│   ├── order.py                     # Order 엔티티 + OrderStatus Enum
│   └── production_job.py            # ProductionJob 엔티티
├── repository/
│   ├── __init__.py
│   ├── sample_repository.py         # JsonDataStore 래핑 시료 저장소
│   ├── order_repository.py          # JsonDataStore 래핑 주문 저장소
│   └── production_repository.py     # FIFO 생산 큐 저장소
├── service/
│   ├── __init__.py
│   ├── sample_service.py            # 시료 관리 비즈니스 로직
│   ├── order_service.py             # 주문 접수/승인/거절 로직
│   ├── production_service.py        # 생산 라인 로직
│   └── release_service.py           # 출고 처리 로직
├── controller/
│   ├── __init__.py
│   ├── main_controller.py           # 메인 루프 + 메뉴 선택
│   ├── sample_controller.py         # 시료 관리 input() 처리
│   ├── order_controller.py          # 주문 접수 input() 처리
│   ├── approval_controller.py       # 주문 승인/거절 input() 처리
│   ├── monitoring_controller.py     # 모니터링 input() 처리
│   ├── production_controller.py     # 생산 라인 input() 처리
│   └── release_controller.py        # 출고 처리 input() 처리
└── view/
    ├── __init__.py
    ├── console_view.py              # 공통 출력 헬퍼 (테이블, 구분선 등)
    ├── sample_view.py               # 시료 관련 print() 전담
    ├── order_view.py                # 주문 관련 print() 전담
    ├── monitoring_view.py           # 모니터링 print() 전담
    ├── production_view.py           # 생산 라인 print() 전담
    └── release_view.py              # 출고 처리 print() 전담
```

---

## 3. 구현 단계

### Phase 1: 모델 정의
**목표:** 핵심 엔티티와 열거형 정의

- [ ] `model/order.py` — `OrderStatus` Enum (RESERVED, REJECTED, PRODUCING, CONFIRMED, RELEASE)
- [ ] `model/sample.py` — `Sample` 데이터클래스 (id, name, avg_production_time, yield_rate, stock)
- [ ] `model/order.py` — `Order` 데이터클래스 (order_id, sample_id, sample_name, customer_name, quantity, status, created_at, updated_at, released_at)
- [ ] `model/production_job.py` — `ProductionJob` 데이터클래스 (job_id, order_id, sample_id, sample_name, order_quantity, shortage, actual_qty, total_time_min, enqueued_at, started_at, estimated_finish, is_running)

**완료 기준:** 모든 엔티티 인스턴스화 가능, 상태 Enum 정상 동작

---

### Phase 2: JsonDataStore 기반 저장소 구현
**목표:** DataPersistence 레포지토리의 JsonDataStore를 래핑해 도메인 객체 CRUD 제공

- [ ] `repository/sample_repository.py` — `JsonDataStore("data/samples.json")` 래핑, 시료 저장·조회·중복 검사
- [ ] `repository/order_repository.py` — `JsonDataStore("data/orders.json")` 래핑, 상태별 조회, 주문번호 생성
- [ ] `repository/production_repository.py` — `JsonDataStore("data/production_jobs.json")` 래핑, FIFO 큐 및 현재 작업 관리

**완료 기준:** 각 저장소 단독 동작 확인, `data/*.json` 파일 생성 확인

---

### Phase 3: 서비스 레이어 구현
**목표:** 비즈니스 로직 캡슐화

- [ ] `service/sample_service.py`
  - 시료 등록 (중복 ID 검증)
  - 시료 목록 조회
  - 이름 기반 검색
- [ ] `service/order_service.py`
  - 주문 접수 (RESERVED 생성)
  - 주문 승인: 재고 충분 → CONFIRMED / 부족 → PRODUCING + 생산 큐 등록
  - 주문 거절 (REJECTED 전환)
- [ ] `service/production_service.py`
  - 실 생산량 계산: `ceil(부족분 / (수율 * 0.9))`
  - 총 생산 시간 계산: `평균 생산시간 * 실 생산량`
  - 생산 완료 처리: PRODUCING → CONFIRMED, 재고 반영
  - 현재 생산 현황 조회
  - 대기 큐 조회
- [ ] `service/release_service.py`
  - CONFIRMED 주문 목록 조회
  - 출고 실행: CONFIRMED → RELEASE, 재고 차감

**완료 기준:** 주문 접수→승인→생산→출고 전체 흐름 서비스 레벨에서 동작

---

### Phase 4: 콘솔 UI 구현 (Controller + View)
**목표:** input()은 controller, print()는 view로 철저히 분리

- [ ] `view/console_view.py` — 공통 출력 헬퍼 (테이블 출력, 구분선, 성공/에러 메시지)
- [ ] `controller/main_controller.py` + (view 없음, 각 하위 컨트롤러 위임)
  - 시스템 요약 출력 요청 → `console_view`, 메뉴 선택
- [ ] `controller/sample_controller.py` + `view/sample_view.py` — 시료 등록 / 목록 / 검색
- [ ] `controller/order_controller.py` + `view/order_view.py` — 주문 접수
- [ ] `controller/approval_controller.py` + (order_view 재사용) — RESERVED 목록 / 승인·거절
- [ ] `controller/monitoring_controller.py` + `view/monitoring_view.py` — 주문 현황 / 재고 현황
- [ ] `controller/production_controller.py` + `view/production_view.py` — 생산 현황 / 대기 큐
- [ ] `controller/release_controller.py` + `view/release_view.py` — CONFIRMED 목록 / 출고 실행

**완료 기준:** 모든 메뉴 화면 진입·입력·출력 정상 동작

---

### Phase 5: 통합 및 검증
**목표:** 전체 흐름 연결 및 엣지 케이스 확인

- [ ] `app.py` — 저장소·서비스·컨트롤러 조립 및 DI
- [ ] `main.py` — `App().run()` 한 줄
- [ ] 시나리오 검증:
  - 시료 등록 → 주문 접수 → 재고 충분 승인 → 출고
  - 시료 등록 → 주문 접수 → 재고 부족 승인 → 생산 완료 → 출고
  - 주문 거절 후 모니터링 미표시 확인
  - 생산 큐 FIFO 순서 확인
  - 재고 상태(여유/부족/고갈) 정확성 확인
  - JSON 파일 재시작 후 데이터 복원 확인

---

## 4. 레이어 간 의존 규칙

```
controller → service → repository → model
```

| 레이어 | 허용 | 금지 |
|--------|------|------|
| `model/` | 도메인 상태, 유효성 검사 | `print()`, `input()`, 타계층 import |
| `view/` | `print()` 출력만 | `input()`, model·controller import |
| `controller/` | `input()` 수신, 흐름 제어, view 호출 | `print()` 직접 호출 |
| `service/` | 비즈니스 로직, repository 호출 | `print()`, `input()` |
| `repository/` | JsonDataStore CRUD 래핑 | `print()`, `input()`, service import |
| `app.py` | 인스턴스 생성 + DI | 비즈니스 로직 |
| `main.py` | `App().run()` 한 줄 | 그 외 |

---

## 5. 주요 비즈니스 로직 공식

| 항목 | 공식 |
|------|------|
| 부족분 | `max(0, 주문수량 - 현재재고)` |
| 실 생산량 | `ceil(부족분 / (수율 * 0.9))` |
| 총 생산 시간 | `평균생산시간(min/ea) × 실 생산량` |
| 재고 상태 판정 | `stock == 0` → 고갈 / `0 < stock < pending_qty` → 부족 / `stock >= pending_qty` → 여유 |
| pending_qty | RESERVED 상태 + PRODUCING 상태 주문의 합산 수량 |
