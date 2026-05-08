# 데이터 모델

## 1. OrderStatus (Enum)

```python
class OrderStatus(Enum):
    RESERVED  = "RESERVED"   # 주문 접수
    REJECTED  = "REJECTED"   # 주문 거절
    PRODUCING = "PRODUCING"  # 생산 중
    CONFIRMED = "CONFIRMED"  # 출고 대기
    RELEASE   = "RELEASE"    # 출고 완료
```

---

## 2. Sample (시료)

```python
@dataclass
class Sample:
    id: str                    # 시료 ID (고유)
    name: str                  # 시료 이름
    avg_production_time: float # 평균 생산시간 (min/ea)
    yield_rate: float          # 수율 (0 < yield_rate <= 1)
    stock: int                 # 현재 재고 수량 (ea)
```

| 필드 | 타입 | 제약 |
|------|------|------|
| id | str | 시스템 내 고유, 중복 불가 |
| name | str | 비어 있으면 안 됨 |
| avg_production_time | float | 양수 |
| yield_rate | float | 0 < value ≤ 1.0 |
| stock | int | 0 이상 정수 |

---

## 3. Order (주문)

```python
@dataclass
class Order:
    order_id: str           # 주문번호 (ORD-YYYYMMDD-NNNN)
    sample_id: str          # 시료 ID (Sample.id 참조)
    sample_name: str        # 시료 이름 (조회 편의)
    customer_name: str      # 고객명
    quantity: int           # 주문 수량 (ea)
    status: OrderStatus     # 현재 주문 상태
    created_at: datetime    # 주문 접수 시각
    updated_at: datetime    # 상태 변경 시각
    released_at: datetime | None  # 출고 처리 시각 (RELEASE 시 기록)
```

| 필드 | 타입 | 제약 |
|------|------|------|
| order_id | str | 시스템 내 고유, 자동 생성 |
| sample_id | str | 등록된 Sample.id 참조 |
| quantity | int | 1 이상 정수 |
| status | OrderStatus | 상태 전이 규칙 준수 |

### 주문번호 생성 규칙
```
ORD-{YYYYMMDD}-{NNNN}
예) ORD-20260508-0001
```
- `YYYYMMDD`: 주문 접수 날짜
- `NNNN`: 당일 0001부터 시작하는 4자리 일련번호

---

## 4. ProductionJob (생산 작업)

```python
@dataclass
class ProductionJob:
    job_id: str              # 작업 ID (자동 생성)
    order_id: str            # 연결된 주문번호
    sample_id: str           # 생산할 시료 ID
    sample_name: str         # 시료 이름 (조회 편의)
    order_quantity: int      # 원래 주문 수량 (ea)
    shortage: int            # 부족분 = max(0, 주문수량 - 승인 시점 재고)
    actual_qty: int          # 실 생산량 = ceil(shortage / (yield_rate * 0.9))
    total_time_min: float    # 총 생산 시간 = avg_production_time * actual_qty
    enqueued_at: datetime    # 큐 등록 시각
    started_at: datetime | None    # 생산 시작 시각
    estimated_finish: datetime | None  # 예상 완료 시각
    is_running: bool         # True: 현재 생산 중 / False: 대기 중
```

| 필드 | 타입 | 설명 |
|------|------|------|
| shortage | int | 승인 시점의 (주문수량 - 현재재고), 최솟값 0 |
| actual_qty | int | ceil(shortage / (yield_rate × 0.9)) |
| total_time_min | float | avg_production_time × actual_qty |
| is_running | bool | 생산 큐에서 현재 처리 중인 작업 여부 |

---

## 5. 인메모리 저장소 구조

### SampleRepository
```python
_samples: dict[str, Sample]   # key: sample.id
```

### OrderRepository
```python
_orders: dict[str, Order]     # key: order.order_id
_daily_counter: dict[str, int] # key: "YYYYMMDD", value: 마지막 일련번호
```

### ProductionRepository
```python
_running: ProductionJob | None    # 현재 생산 중인 작업
_queue: deque[ProductionJob]      # 대기 큐 (FIFO)
```

---

## 6. 엔티티 간 관계

```
Sample (1) ──────────────── (N) Order
       └── sample_id 참조

Order (1) ──────────────── (0..1) ProductionJob
      └── order_id 참조
      (PRODUCING 상태인 주문만 ProductionJob 보유)
```
