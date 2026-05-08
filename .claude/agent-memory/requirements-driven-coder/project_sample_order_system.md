---
name: SampleOrderSystem Project Context
description: 반도체 시료 생산주문관리 시스템 — 구현 완료 상태, 주요 설계 결정 및 제약
type: project
---

Phase 1~5 TDD 구현 완료 (2026-05-08).

- DataPersistence-dongyeb-20020057 패키지가 venv에 미설치되어 있어, `data_store.py`와 `exceptions.py`를 프로젝트 루트에 직접 구현함.
- Python 3.14.4 사용 (match-case 사용 가능).
- pytest 9.0.3 설치됨.

**Why:** DataPersistence 패키지를 GitHub에서 직접 클론하지 않고 CLAUDE.md의 API 명세를 기반으로 로컬 구현함.
**How to apply:** 향후 DataPersistence 패키지가 설치되면 `data_store.py`와 `exceptions.py`를 삭제하고 import 경로만 수정하면 됨.

계층 경계 규칙이 테스트로 검증됨 (AST 파싱 기반, encoding="utf-8" 필수).
