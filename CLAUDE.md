# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

반도체 시료 생산주문관리 시스템 — 콘솔(CLI) 기반 Python 애플리케이션.  
요구사항은 `PRD.md`, 구현 계획은 `PLAN.md`, 설계 문서는 `docs/design/`에 위치한다.

## 실행 방법

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 실행
python main.py
```

## 참조 레포지토리 및 활용 지침

구현 시 아래 4개 레포지토리의 코드와 패턴을 **직접 참조·통합**한다.  
각 레포지토리를 클론하거나 소스를 복사해 이 프로젝트에 맞게 적용한다.

### 1. MVC 스켈레톤 — `ConsoleMVC-dongyeb-20020057` (master 브랜치)
> https://github.com/dongyub1015/ConsoleMVC-dongyeb-20020057

- `app.py`의 DI Root 패턴을 그대로 사용한다: 저장소 → 서비스 → 컨트롤러 순으로 생성·주입.
- `controller/todo_controller.py`의 `match-case` 메뉴 디스패치 패턴을 모든 컨트롤러에 적용한다.
- `model/todo_repository.py`의 Repository ABC + InMemory 구현체 패턴을 `repository/` 레이어에 적용한다.
- **계층 경계 규칙** (위반 금지):

  | 계층 | 허용 | 금지 |
  |------|------|------|
  | `model/` | 도메인 상태, 유효성 검사 | `print()`, `input()`, 타계층 import |
  | `view/` | `print()` 출력만 | `input()`, model·controller import |
  | `controller/` | `input()` 수신, 흐름 제어, view 호출 | `print()` 직접 호출 |
  | `service/` | 비즈니스 로직, repository 호출 | `print()`, `input()` |
  | `repository/` | JsonDataStore CRUD 래핑 | `print()`, `input()`, service import |
  | `app.py` | 인스턴스 생성 + DI | 비즈니스 로직 |

### 2. 데이터 영속성 — `DataPersistence-dongyeb-20020057` (master 브랜치)
> https://github.com/dongyub1015/DataPersistence-dongyeb-20020057

- `data_store.py`의 `JsonDataStore` 클래스를 `repository/` 구현체의 영속성 백엔드로 사용한다.
- `exceptions.py`의 `DuplicateKeyError`, `RecordNotFoundError`를 그대로 사용한다.
- `JsonDataStore` 핵심 API:
  - `create(record: dict, record_id: str | None)` → 자동 ID 생성 또는 지정 ID 사용
  - `read(record_id: str)` → 단건 조회, 없으면 `RecordNotFoundError`
  - `read_all()` → 전체 레코드 반환
  - `update(record_id: str, fields: dict)` → 지정 필드만 업데이트, ID 보호
  - `delete(record_id: str)` → 삭제
- 각 엔티티(Sample, Order, ProductionJob)마다 별도 JSON 파일로 분리한다.  
  예: `data/samples.json`, `data/orders.json`, `data/production_jobs.json`

### 3. 데이터 모니터링 Tool — `DataMonitor-dongyeb-20020057` (master 브랜치)
> https://github.com/dongyub1015/DataMonitor-dongyeb-20020057

- 모니터링 메뉴(`[4] 모니터링`)의 주문 현황·재고량 출력 형식에 DataMonitor의 TUI 위젯 또는 출력 패턴을 참조한다.
- DataMonitor의 `DataSource` ABC를 참고해 `JsonDataStore` 기반 커스텀 소스를 구현한다.
- 최소 터미널 크기 80×24를 준수한다.
- 실행: `python -m datamonitor --config config.yaml` (모니터링 독립 실행 시)

### 4. Dummy 데이터 생성 Tool — `DummyDataGenerator-dongyeb-20020057` (master 브랜치)
> https://github.com/dongyub1015/DummyDataGenerator-dongyeb-20020057

- 개발·테스트용 시료/주문 더미 데이터 생성에 사용한다.
- `config.yaml` 형식으로 시료(Sample), 주문(Order) 테이블 구조를 정의한다.
- 로케일은 `ko_KR`, 시드는 고정값을 사용해 재현 가능한 데이터를 생성한다.
- 실행: `python -m dummy_gen run --config config.yaml`

## 아키텍처

```
main.py
  └── app.py  (DI Root: 저장소 → 서비스 → 뷰 → 컨트롤러 생성 및 주입)
        ├── model/         도메인 엔티티 + OrderStatus Enum
        ├── repository/    JsonDataStore 래핑 CRUD (ABC + 구현체)
        ├── service/       비즈니스 로직 (주문 승인 분기, 생산량 계산 등)
        ├── controller/    input() 수신 + 메뉴 흐름 제어
        └── view/          print() 전담 출력
```

의존 방향: `controller → service → repository → model`  
`view`는 `controller`가 데이터를 넘겨 호출하며, `view`는 어떤 레이어도 import하지 않는다.

## 핵심 비즈니스 로직

주문 승인 시 재고 분기와 생산량 계산은 `service/order_service.py`와 `service/production_service.py`에 집중한다.

```python
from math import ceil

shortage = max(0, order.quantity - sample.stock)
actual_qty = ceil(shortage / (sample.yield_rate * 0.9))
total_time_min = sample.avg_production_time * actual_qty
```

생산 큐는 `collections.deque`(FIFO)로 구현하며, 한 번에 하나의 작업만 `is_running=True` 상태를 가진다.

## 주문 상태 전이

```
RESERVED ──[승인, 재고 충분]──► CONFIRMED ──[출고]──► RELEASE
RESERVED ──[승인, 재고 부족]──► PRODUCING ──[생산 완료]──► CONFIRMED
RESERVED ──[거절]────────────► REJECTED  (종단, 모니터링 제외)
```

상태 변경은 반드시 `service` 레이어에서만 수행한다. `controller`가 직접 `Order.status`를 변경하지 않는다.

## 주문번호 생성

```python
# ORD-YYYYMMDD-NNNN 형식, OrderRepository 내부에서 처리
from datetime import date
order_id = f"ORD-{date.today().strftime('%Y%m%d')}-{counter:04d}"
```

## 재고 상태 판정 (모니터링)

| 상태 | 조건 |
|------|------|
| 고갈 | `stock == 0` |
| 부족 | `0 < stock < pending_quantity` |
| 여유 | `stock >= pending_quantity` |

`pending_quantity`는 RESERVED + PRODUCING 상태 주문의 합산 수량이다.
