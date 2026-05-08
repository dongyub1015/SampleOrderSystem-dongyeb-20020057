# 반도체 시료 생산주문관리 시스템

가상의 반도체 회사 **S Semi**의 시료 생산·주문·출고 전 과정을 관리하는 콘솔(CLI) 기반 Python 애플리케이션입니다.

## 실행 방법

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 실행
python main.py
```

> Python 3.10 이상 필요. 외부 패키지 의존성 없음 (표준 라이브러리만 사용).

## 주요 기능

| 메뉴 | 기능 |
|------|------|
| [1] 시료 관리 | 시료 등록, 목록 조회, 이름 검색 |
| [2] 시료 주문 | 주문 접수 (RESERVED 상태 생성) |
| [3] 주문 승인/거절 | 재고 충분 → CONFIRMED / 부족 → PRODUCING + 생산 큐 등록 |
| [4] 모니터링 | 상태별 주문 현황, 시료별 재고 현황 (여유/부족/고갈) |
| [5] 생산라인 조회 | 현재 생산 중인 작업 + FIFO 대기 큐 표시, 생산 완료 처리 |
| [6] 출고 처리 | CONFIRMED 주문 목록 번호 선택 후 출고 (RELEASE) |

## 주문 상태 흐름

```
RESERVED ──[승인, 재고 충분]──► CONFIRMED ──[출고]──► RELEASE
RESERVED ──[승인, 재고 부족]──► PRODUCING ──[생산 완료]──► CONFIRMED
RESERVED ──[거절]────────────► REJECTED
```

## 아키텍처

레이어드 아키텍처 (MVC 기반) — 각 레이어는 바로 아래 레이어만 참조합니다.

```
controller/  ← input() 수신, 메뉴 흐름 제어
view/        ← print() 전담 출력
service/     ← 비즈니스 로직
repository/  ← JsonDataStore CRUD 래핑
model/       ← 도메인 엔티티 (Sample, Order, ProductionJob)
```

```
main.py → app.py (DI Root) → controller → service → repository → model
```

데이터는 `data/` 디렉토리의 JSON 파일로 영속 저장됩니다 (`data/samples.json`, `data/orders.json`, `data/production_jobs.json`).

## 핵심 비즈니스 로직

```python
from math import ceil

# 가용 재고 = 현재 재고 - CONFIRMED 선점 수량
available_stock = sample.stock - confirmed_reserved

# 생산 수량 계산 (수율·오차 보정)
shortage   = max(0, order.quantity - available_stock)
actual_qty = ceil(shortage / (sample.yield_rate * 0.9))
total_time = sample.avg_production_time * actual_qty  # 분 단위
```

생산 큐는 **FIFO** 방식으로 스케줄링되며, 한 번에 하나의 작업만 실행됩니다.

## 프로젝트 구조

```
SampleOrderSystem/
├── main.py                  # 진입점
├── app.py                   # DI Root
├── model/                   # 도메인 엔티티
├── repository/              # JsonDataStore 래핑 저장소
├── service/                 # 비즈니스 로직
├── controller/              # input() 처리
├── view/                    # print() 출력
├── data_store.py            # JSON 저장소 구현
├── exceptions.py            # 커스텀 예외
└── tests/                   # pytest 테스트 (104개)
```

## 테스트 실행

```bash
python -m pytest tests/
```

104개 테스트, Phase 1~5 전체 커버리지.
