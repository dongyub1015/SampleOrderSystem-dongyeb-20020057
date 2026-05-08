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

**2차 검증 (2026-05-08) 잔여 이슈 4건 — 3차 검증에서 전원 해소 확인:**
1. CLAUDE.md 계층 경계 규칙 표에 service/ 레이어 행 추가 → 해소됨
2. CLAUDE.md 아키텍처 다이어그램에 repository/ 레이어 추가 → 해소됨
3. state-machine.md 섹션 5 순차 처리 가정 명시 → 해소됨
4. ui-flow.md 2.5절 수식 주석 max(0,...) 추가 → 해소됨

**3차 검증 (2026-05-08) 잔여 이슈 3건:**
1. [🟠 높음] PLAN.md app.py 주석 및 Phase 5 체크리스트에 view 레이어 DI 누락 (CLAUDE.md/architecture.md는 "저장소→서비스→뷰→컨트롤러" 명시)
2. [🟡 보통] ui-flow.md 2.5절 total_time_min 표시 시 반올림 규칙 미명시 (0.8*61=48.8 → 49로 표시되나 ceil/round 불명확)
3. [🟡 보통] state-machine.md 3.1절(RESERVED→CONFIRMED) 재고 선점 처리 여부 미명시 — 출고(3.5절)에만 stock 차감 명시되어 있고 승인 시 선점 없음이 암묵적

**확정된 핵심 용어 및 공식:**
- 레이어 명칭: model / repository / service / controller / view / app.py / main.py
- pending_qty = RESERVED 상태 주문 수량 합 + PRODUCING 상태 주문 수량 합
- shortage = max(0, 주문수량 - 현재재고)
- actual_qty = ceil(shortage / (yield_rate * 0.9))
- total_time_min = avg_production_time * actual_qty (표시 반올림 규칙 미확정)
- 메인 메뉴: [1]시료관리, [2]시료주문, [3]주문승인/거절, [4]모니터링, [5]생산라인조회, [6]출고처리, [0]종료

**Why:** 3차 검증 세션 — 2차에서 발견된 4건 수정 후 잔여 이슈 확인
**How to apply:** 다음 세션에서 위 3건 해소 여부를 재확인; PLAN.md view DI 추가가 최우선 조치
