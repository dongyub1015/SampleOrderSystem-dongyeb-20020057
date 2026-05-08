# PLAN: 반도체 시료 생산주문관리 시스템 구현 계획

## 1. 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.10+ |
| 데이터 저장 | 인메모리 (dict / list) |
| 외부 의존성 | 없음 (표준 라이브러리만 사용) |
| 실행 방식 | `python main.py` |

---

## 2. 디렉토리 구조

```
SampleOrderSystem/
├── main.py                          # 진입점
├── PRD.md
├── PLAN.md
├── docs/
│   └── design/
│       ├── architecture.md
│       ├── data-model.md
│       ├── state-machine.md
│       └── ui-flow.md
├── domain/
│   ├── __init__.py
│   ├── sample.py                    # Sample 엔티티
│   ├── order.py                     # Order 엔티티 + OrderStatus Enum
│   └── production_job.py            # ProductionJob 엔티티
├── repository/
│   ├── __init__.py
│   ├── sample_repository.py         # 시료 인메모리 저장소
│   ├── order_repository.py          # 주문 인메모리 저장소
│   └── production_repository.py     # 생산 큐 저장소
├── service/
│   ├── __init__.py
│   ├── sample_service.py            # 시료 관리 비즈니스 로직
│   ├── order_service.py             # 주문 접수/승인/거절 로직
│   ├── production_service.py        # 생산 라인 로직
│   └── release_service.py           # 출고 처리 로직
└── ui/
    ├── __init__.py
    ├── console.py                   # 공통 입출력 유틸
    ├── main_menu.py                 # 메인 메뉴
    ├── sample_menu.py               # 시료 관리 메뉴
    ├── order_menu.py                # 주문 접수/승인/거절 메뉴
    ├── monitoring_menu.py           # 모니터링 메뉴
    ├── production_menu.py           # 생산 라인 메뉴
    └── release_menu.py              # 출고 처리 메뉴
```

---

## 3. 구현 단계

### Phase 1: 도메인 모델 정의
**목표:** 핵심 엔티티와 열거형 정의

- [ ] `domain/order.py` — `OrderStatus` Enum (RESERVED, REJECTED, PRODUCING, CONFIRMED, RELEASE)
- [ ] `domain/sample.py` — `Sample` 데이터클래스 (id, name, avg_production_time, yield_rate, stock)
- [ ] `domain/order.py` — `Order` 데이터클래스 (order_id, sample_id, customer_name, quantity, status, created_at)
- [ ] `domain/production_job.py` — `ProductionJob` 데이터클래스 (job_id, order_id, sample_id, shortage, actual_qty, estimated_finish, status)

**완료 기준:** 모든 엔티티 인스턴스화 가능, 상태 Enum 정상 동작

---

### Phase 2: 인메모리 저장소 구현
**목표:** 도메인 객체의 CRUD 및 조회 기능 제공

- [ ] `repository/sample_repository.py` — 시료 저장, 조회, 중복 검사
- [ ] `repository/order_repository.py` — 주문 저장, 상태별 조회, 주문번호 생성
- [ ] `repository/production_repository.py` — FIFO 생산 큐, 현재 작업 관리

**완료 기준:** 각 저장소 단독 동작 확인

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

### Phase 4: 콘솔 UI 구현
**목표:** 담당자가 사용하는 메뉴 화면 구현

- [ ] `ui/console.py` — 공통 입력/출력 헬퍼 (메뉴 선택, 테이블 출력 등)
- [ ] `ui/main_menu.py` — 시스템 요약 + 메뉴 선택
- [ ] `ui/sample_menu.py` — 시료 등록 / 목록 / 검색
- [ ] `ui/order_menu.py` — 주문 접수 / RESERVED 목록 / 승인·거절
- [ ] `ui/monitoring_menu.py` — 주문 현황 / 재고 현황(여유·부족·고갈)
- [ ] `ui/production_menu.py` — 생산 현황 / 대기 큐
- [ ] `ui/release_menu.py` — CONFIRMED 목록 / 출고 실행

**완료 기준:** 모든 메뉴 화면 진입·입력·출력 정상 동작

---

### Phase 5: 통합 및 검증
**목표:** 전체 흐름 연결 및 엣지 케이스 확인

- [ ] `main.py` — 저장소·서비스·메뉴 조립 및 루프 실행
- [ ] 시나리오 검증:
  - 시료 등록 → 주문 접수 → 재고 충분 승인 → 출고
  - 시료 등록 → 주문 접수 → 재고 부족 승인 → 생산 완료 → 출고
  - 주문 거절 후 모니터링 미표시 확인
  - 생산 큐 FIFO 순서 확인
  - 재고 상태(여유/부족/고갈) 정확성 확인

---

## 4. 레이어 간 의존 규칙

```
UI → Service → Repository → Domain
```

- UI는 Service만 호출, Repository를 직접 참조하지 않는다
- Service는 Repository를 통해서만 데이터에 접근한다
- Domain 객체는 어떤 레이어도 참조하지 않는다

---

## 5. 주요 비즈니스 로직 공식

| 항목 | 공식 |
|------|------|
| 부족분 | `max(0, 주문수량 - 현재재고)` |
| 실 생산량 | `ceil(부족분 / (수율 * 0.9))` |
| 총 생산 시간 | `평균생산시간(min/ea) × 실 생산량` |
| 재고 상태 판정 | 재고=0 → 고갈 / 재고<주문대기량 → 부족 / 그 외 → 여유 |
