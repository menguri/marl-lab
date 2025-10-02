#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH_DIR="$PROJECT_ROOT/patches/pymarl2"
SUBMODULE_DIR="$PROJECT_ROOT/external/pymarl2"

if [ ! -d "$PATCH_DIR" ]; then
  echo "[apply_pymarl2_patches] 패치 디렉토리를 찾을 수 없습니다: $PATCH_DIR" >&2
  exit 1
fi

if [ ! -d "$SUBMODULE_DIR" ]; then
  echo "[apply_pymarl2_patches] PyMARL2 서브모듈이 없습니다: $SUBMODULE_DIR" >&2
  exit 1
fi

cd "$SUBMODULE_DIR"
for patch_file in "$PATCH_DIR"/*.patch; do
  [ -e "$patch_file" ] || continue
  if git apply --check "$patch_file" >/dev/null 2>&1; then
    echo "Applying $(basename "$patch_file")"
    git apply --whitespace=fix "$patch_file"
  else
    echo "Skipping $(basename "$patch_file") (already applied?)"
  fi
done

printf '\nPyMARL2 패치 적용 완료\n'
