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
- 주문번호: ORD-YYYYMMDD-NNNN, _daily_counter는 메모리 캐시 (재시작 시 _restore_counter()로 복원됨 — 2차 검증에서 해결 확인)
- 생산 큐: is_running=True 단 1개, 나머지 is_running=False (enqueued_at ASC FIFO)
- estimated_finish: 2차 수정에서 ProductionService._calculate_estimated_finish()로 구현됨

2차 검증(2026-05-08)에서 해결된 항목:
1. controller 레이어 print() 직접 호출 — 전체 제거 확인 (grep 결과 0건)
2. approval_controller.py — 번호 선택 UX로 재설계 완료
3. production_controller.py — 자동 표시 후 [C]/[Enter] 선택으로 재설계 완료
4. release_controller.py — 번호 선택 UX로 재설계 완료
5. estimated_finish — _calculate_estimated_finish() 메서드 구현 완료
6. _restore_counter() — 재시작 시 일련번호 복원 정상 동작 확인

2차 검증에서 신규 발견된 위반:
- console_view.py의 print_title()이 인자 없는 시그니처인데, 다른 뷰들이 print_title("제목") 형식으로 인자를 전달 → TypeError 런타임 오류 발생
  - 영향 뷰: monitoring_view, order_view, production_view, release_view (총 9개 호출 지점)
  - 테스트는 단독 print_title() 호출만 검증해 탐지 못함
  - 수정 방법: print_title(self, title: str = "") 로 시그니처 변경 또는 각 뷰에서 print_title 직전 별도 출력

지속 미해결 항목:
- 페이지네이션(20건 초과 시 [N]/[P]) 미구현 — ui-flow.md 공통 UX 규칙
- order_controller.py에 ui-flow.md에 없는 [2] 전체 주문 조회 메뉴 존재 (초과 구현, 기능 자체는 무해)
- approval_controller.py에서 재고 확인 중/부족분 상세 출력 없음 (ui-flow.md [3] 명세와 부분 차이)
