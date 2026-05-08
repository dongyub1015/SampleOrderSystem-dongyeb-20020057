---
name: pre-pr-cleanup
description: PR 생성 전, 설계 문서(PLAN.md, docs/design/*.md)를 git에서 삭제하는 커밋을 만든다. 파일 추가 이력은 이전 커밋에 보존된다.
---

# PR 전 설계 문서 정리

## 목적

`PLAN.md`와 `docs/design/*.md`는 개발 과정의 내부 설계 산출물이다.  
PR에는 포함하지 않되, 추가했던 커밋 이력은 남긴다.

## 실행 절차

### 1단계: 삭제 대상 확인

아래 파일이 git에 추적되고 있는지 확인한다.

```bash
git ls-files PLAN.md docs/design/
```

출력이 비어 있으면 이미 추적되지 않는 상태이므로 중단한다.

### 2단계: git에서 삭제 (로컬 파일도 함께 삭제)

```bash
git rm PLAN.md docs/design/architecture.md docs/design/data-model.md docs/design/state-machine.md docs/design/ui-flow.md
```

파일이 일부만 존재할 경우 존재하는 파일만 대상으로 실행한다.

### 3단계: 커밋 생성

```bash
git commit -m "chore: remove design documents before PR

PLAN.md and docs/design/*.md are internal planning artifacts.
Removed from the branch to keep the PR diff clean.
History of their addition is preserved in prior commits."
```

### 4단계: 결과 확인

```bash
git log --oneline -3
git status
```

`PLAN.md`와 `docs/design/` 이 working tree에서 사라지고,  
삭제 커밋이 log에 기록되면 완료다.

## 주의사항

- 이 작업은 **되돌리기 어렵다**. 실행 전 현재 브랜치가 맞는지 확인한다.
- 삭제 전 파일 내용을 보존하려면 별도 백업하거나 이전 커밋에서 복구한다: `git show HEAD~1:PLAN.md`
- `main` / `master` 브랜치에서는 직접 실행하지 않는다. 반드시 feature 브랜치에서 실행한다.
