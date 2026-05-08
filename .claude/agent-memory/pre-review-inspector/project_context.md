---
name: SampleOrderSystem 프로젝트 컨텍스트
description: 반도체 시료 생산주문관리 시스템의 아키텍처, 도메인 규칙, 기술 스택
type: project
---

반도체 시료(Sample) 생산·주문·출고를 관리하는 콘솔 기반 Python 애플리케이션.

**Why:** 학습/과제용 프로젝트로 추정. DataPersistence 외부 패키지를 로컬 구현으로 대체함.

**기술 스택:** Python (dataclass, Enum, match-case), JSON 파일 기반 저장소, pytest

**계층 구조:** model → repository → service → controller → view (엄격한 단방향 의존)

**핵심 비즈니스 규칙:**
- 실 생산량: ceil(부족분 / (수율 * 0.9))
- pending_qty = RESERVED + PRODUCING 상태 주문 수량 합산
- 주문 상태 전이: RESERVED → CONFIRMED (재고 충분) or PRODUCING (부족) → CONFIRMED (생산완료) → RELEASE
- RESERVED 상태만 승인/거절 가능, CONFIRMED 상태만 출고 가능

**How to apply:** 리뷰 시 계층 경계 위반(print/input 직접 호출 위치), 상태 전이 규칙, 수식 정확성을 최우선으로 점검.
