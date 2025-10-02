#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH_DIR="$PROJECT_ROOT/patches/marllib"
SUBMODULE_DIR="$PROJECT_ROOT/external/marllib"

[ -d "$PATCH_DIR" ]     || { echo "[ERR] no patch dir: $PATCH_DIR" >&2; exit 1; }
[ -d "$SUBMODULE_DIR" ] || { echo "[ERR] no submodule: $SUBMODULE_DIR" >&2; exit 1; }

cd "$SUBMODULE_DIR"

apply_one() {
  local pf="$1"
  # mbox 여부: 첫 줄이 "From <sha>" 형식이면 mbox
  if head -n1 "$pf" | grep -qE '^From [0-9a-f]{7,} '; then
    echo "[AM ] $(basename "$pf")"
    # 3-way로 시도
    if ! git am -3 "$pf"; then
      echo "[FAIL] git am failed: $pf" >&2
      git am --abort || true
      return 1
    fi
  else
    echo "[APPLY] $(basename "$pf")"
    # 인덱스+3way로 적용 → 나중에 커밋 가능
    if ! git apply --index --3way --whitespace=fix "$pf"; then
      echo "[FAIL] git apply failed (not already-applied): $pf" >&2
      return 1
    fi
  fi
}

shopt -s nullglob
changed=false
for patch_file in "$PATCH_DIR"/*.patch "$PATCH_DIR"/*.diff; do
  # 먼저 "이미 적용됨" 탐지: 시그니처 문자열 기반(있으면 스킵)
  # 예: 문제였던 import 라인 같은 키워드로 커스텀 스킵 규칙을 넣을 수도 있음
  if apply_one "$patch_file"; then
    changed=true
  else
    echo "[WARN] Skipping due to failure (check patch/base mismatch): $(basename "$patch_file")"
  fi
done

if $changed; then
  # 변경이 있다면 커밋(옵션)
  if ! git diff --staged --quiet; then
    git commit -m "Apply marllib patches from $(realpath --relative-to="$PROJECT_ROOT" "$PATCH_DIR")"
  fi
fi

echo "MARLlib 패치 적용 완료"
