# 주문 상태 머신 (Order State Machine)

## 1. 상태 전이 다이어그램

```
                      ┌──────────┐
                      │  시작    │
                      └────┬─────┘
                           │ 주문 접수
                           ▼
                    ┌─────────────┐
                    │  RESERVED   │  ← 주문 접수 완료
                    └──────┬──────┘
            ┌──────────────┼──────────────┐
            │ [승인]        │ [승인]       │ [거절]
            │ 재고 충분     │ 재고 부족    │
            ▼              ▼              ▼
     ┌───────────┐  ┌──────────────┐  ┌──────────┐
     │ CONFIRMED │  │  PRODUCING   │  │ REJECTED │ ← 종단 상태
     └─────┬─────┘  └──────┬───────┘  └──────────┘
           │         생산 완료│
           │  ◄────────────┘
           │ [출고]
           ▼
      ┌─────────┐
      │ RELEASE │  ← 종단 상태
      └─────────┘
```

---

## 2. 상태별 정의

| 상태 | 진입 조건 | 다음 상태 | 모니터링 포함 |
|------|-----------|-----------|:---:|
| RESERVED | 주문 접수 시 자동 설정 | CONFIRMED, PRODUCING, REJECTED | O |
| REJECTED | 담당자가 거절 처리 | (종단) | X |
| PRODUCING | 승인 + 재고 부족 | CONFIRMED | O |
| CONFIRMED | 승인 + 재고 충분, 또는 생산 완료 | RELEASE | O |
| RELEASE | 출고 처리 완료 | (종단) | O |

---

## 3. 전이 조건 및 액션

### 3.1 RESERVED → CONFIRMED
- **트리거:** 담당자가 주문 승인 실행
- **가드:** `현재 재고 >= 주문 수량`
- **액션:**
  1. `Order.status = CONFIRMED`
  2. `Order.updated_at = now()`

### 3.2 RESERVED → PRODUCING
- **트리거:** 담당자가 주문 승인 실행
- **가드:** `현재 재고 < 주문 수량`
- **액션:**
  1. `Order.status = PRODUCING`
  2. `Order.updated_at = now()`
  3. `shortage = max(0, quantity - stock)`
  4. `actual_qty = ceil(shortage / (yield_rate * 0.9))`
  5. `total_time_min = avg_production_time * actual_qty`
  6. `ProductionJob` 생성 후 생산 큐(FIFO) 말단에 추가

### 3.3 RESERVED → REJECTED
- **트리거:** 담당자가 주문 거절 실행
- **가드:** 없음
- **액션:**
  1. `Order.status = REJECTED`
  2. `Order.updated_at = now()`

### 3.4 PRODUCING → CONFIRMED
- **트리거:** 생산 완료 (담당자가 생산 완료 처리 실행)
- **가드:** 해당 주문의 `ProductionJob`이 존재
- **액션:**
  1. `Order.status = CONFIRMED`
  2. `Order.updated_at = now()`
  3. `Sample.stock += actual_qty` (생산된 수량 재고 반영)
  4. `ProductionJob` 완료 처리 (큐에서 제거, 다음 작업 시작)
- **불변식:** `actual_qty = ceil(shortage / (yield * 0.9)) >= shortage`이므로, 생산 완료 후 `stock >= quantity`가 보장된다. CONFIRMED → RELEASE 출고 시 재고 부족 상황은 발생하지 않는다.

### 3.5 CONFIRMED → RELEASE
- **트리거:** 담당자가 출고 처리 실행
- **가드:** `Order.status == CONFIRMED`
- **액션:**
  1. `Order.status = RELEASE`
  2. `Order.released_at = now()`
  3. `Order.updated_at = now()`
  4. `Sample.stock -= quantity` (출고 수량 재고 차감)

---

## 4. 유효하지 않은 전이 (방어 처리 필요)

| 시도 | 이유 |
|------|------|
| REJECTED → 임의 상태 | REJECTED는 종단 상태 |
| RELEASE → 임의 상태 | RELEASE는 종단 상태 |
| CONFIRMED → PRODUCING | 이미 재고 확보 완료 |
| PRODUCING → REJECTED | 생산 중 거절 불가 |

---

## 5. 생산 큐 스케줄링

```
생산 큐 (deque, FIFO)
┌────────────────────────────────────────┐
│  RUNNING  │  WAITING[0]  │  WAITING[1] │ ...
│  Job #1   │   Job #2     │   Job #3    │
└────────────────────────────────────────┘
                    ↑
        생산 완료 시 WAITING[0]이 RUNNING으로 승격
```

- 한 번에 하나의 `ProductionJob`만 `is_running=True` 상태
- 생산 완료 후 자동으로 큐의 다음 작업 시작 (`enqueued_at` ASC 정렬)
- 대기 중 작업의 `estimated_finish`는 앞선 작업들의 `total_time_min` 합산으로 계산
- 동시 주문 처리는 순차 처리로 가정 — 재고 잠금(reserved_stock) 메커니즘 불필요
