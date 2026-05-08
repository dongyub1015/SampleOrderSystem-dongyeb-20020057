---
name: SampleOrderSystem 프로젝트 개요
description: 반도체 시료 생산주문관리 시스템 문서 검증 세션 기록 — 문서 구성, 핵심 용어 합의, 충돌 패턴 및 해소 현황
type: project
---

반도체 시료 생산주문관리 시스템(SampleOrderSystem) — 콘솔(CLI) 기반 Python 애플리케이션.

**검증 대상 문서 (2026-05-08 기준):**
- PLAN.md: 디렉토리 구조, 레이어 의존 규칙, 비즈니스 로직 공식, 구현 단계
- CLAUDE.md: 아키텍처 설명, 계층 경계 규칙, 핵심 비즈니스 로직, 참조 레포지토리 지침
- docs/design/architecture.md: 레이어드 아키텍처, 컴포넌트 다이어그램, 디렉토리 구조
- docs/design/data-model.md: 엔티티 필드 정의, OrderStatus Enum, 저장소 구조
- docs/design/state-machine.md: 상태 전이 조건 및 액션
- docs/design/ui-flow.md: 메뉴 계층 및 화면 명세

**1차 검증 (2026-05-08) 이후 수정 완료된 주요 사항:**
1. CLAUDE.md 아키텍처가 model/repository/service/controller/view 5계층으로 수정됨 (이전: model/view/controller만 언급)
2. CLAUDE.md가 JsonDataStore 영속성 백엔드를 명시함 (이전: 불일치)
3. pending_qty = RESERVED + PRODUCING 공식이 PLAN.md, CLAUDE.md에 통일됨

**2차 검증 (2026-05-08) 에서 발견된 잔여 이슈:**
1. CLAUDE.md 계층 경계 규칙 표에 service/ 레이어 행이 누락됨 (PLAN.md/architecture.md에는 존재)
2. CLAUDE.md 아키텍처 다이어그램에 repository/ 레이어가 누락됨
3. state-machine.md 섹션 5에서 "동시 주문 처리는 순차 처리로 가정 — 재고 잠금(reserved_stock) 메커니즘 불필요"라고 명시하나, CLAUDE.md/PLAN.md는 pending_qty 계산으로 재고 경합을 간접 처리하는 설계를 내포함 (미미한 모호성)
4. ui-flow.md 2.5절 생산라인 조회 화면의 수식 주석이 "부족분 = 주문량 - 재고" (max(0,...) 누락)

**확정된 핵심 용어 및 공식:**
- 레이어 명칭: model / repository / service / controller / view / app.py / main.py
- pending_qty = RESERVED 상태 주문 수량 합 + PRODUCING 상태 주문 수량 합
- shortage = max(0, 주문수량 - 현재재고)
- actual_qty = ceil(shortage / (yield_rate * 0.9))
- total_time_min = avg_production_time * actual_qty
- 메인 메뉴: [1]시료관리, [2]시료주문, [3]주문승인/거절, [4]모니터링, [5]생산라인조회, [6]출고처리, [0]종료

**Why:** 2차 검증 세션 — 1차에서 발견된 12건 수정 후 잔여 이슈 확인
**How to apply:** 다음 세션에서 위 잔여 이슈 해소 여부를 재확인; CLAUDE.md service/ 행 추가 및 아키텍처 다이어그램 repository/ 추가가 핵심 조치
