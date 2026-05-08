---
name: SampleOrderSystem 프로젝트 컨텍스트
description: 반도체 시료 생산주문관리 시스템의 구조, 검증 기준 문서 위치, 핵심 설계 결정 사항
type: project
---

반도체 시료 생산주문관리 시스템 (콘솔 CLI, Python 3.10+) 프로젝트.

**Why:** PLAN.md Phase 1~5 체크리스트 기반 구현 검증이 주요 목적이며, MVC 패턴과 JsonDataStore 기반 영속성을 사용한다.

**How to apply:** 검증 시 PLAN.md, CLAUDE.md, docs/design/ 하위 4개 문서를 기준으로 한다. 계층 경계 위반(print/input 혼용)이 핵심 체크 포인트다.

주요 설계 결정:
- data_store.py / exceptions.py는 DataPersistence-dongyeb-20020057 레포지토리를 로컬 복사하여 사용
- 레이어: model → repository → service → controller, view는 controller가 데이터를 넘겨 호출
- OrderStatus: RESERVED, REJECTED, PRODUCING, CONFIRMED, RELEASE
- 주문번호: ORD-YYYYMMDD-NNNN, _daily_counter는 메모리 캐시 (재시작 시 카운터 초기화 문제 있음)
- 생산 큐: is_running=True 단 1개, 나머지 is_running=False (enqueued_at ASC FIFO)
- estimated_finish는 항상 None으로 저장됨 — ui-flow.md 명세 미충족

검증 시 발견된 주요 위반:
1. controller 레이어 전체(approval, monitoring, order, production, release)에서 print() 직접 호출 — CLAUDE.md/PLAN.md 계층 경계 위반
2. [3] 승인/거절 메뉴가 ui-flow.md 명세(번호 선택 방식)와 달리 주문번호 직접 입력 방식으로 구현됨
3. [5] 생산라인 조회가 ui-flow.md 명세(자동 표시 후 뒤로)와 달리 3개 서브메뉴를 가짐
4. estimated_finish가 항상 None — 대기 작업의 예상 완료 시각 계산 로직 미구현
5. _daily_counter가 메모리 캐시라 재시작 시 당일 카운터 초기화 — 주문번호 중복 위험
6. 페이지네이션(20건 초과 시 [N]/[P]) 미구현 — ui-flow.md 공통 UX 규칙
