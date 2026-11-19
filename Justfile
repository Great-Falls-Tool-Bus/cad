default:
    @just --list

setup: hooks-install

hooks-install:
    #!/usr/bin/env bash
    set -euo pipefail
    git config --local core.hooksPath .githooks
    git config --local remote.pushDefault origin
    if git remote get-url upstream >/dev/null 2>&1; then
        git remote set-url --push upstream DISABLED-fork-first
    fi
    if [[ "$(git config --bool --get commit.gpgsign || true)" != true ]]; then
        echo "Set commit.gpgsign to true and configure your signing key before committing." >&2
    fi

hooks-check:
    #!/usr/bin/env bash
    set -euo pipefail
    scratch="$(mktemp -d)"
    trap 'rm -rf "$scratch"' EXIT
    git clone --quiet --depth 1 --filter=blob:none --no-checkout --branch main https://github.com/Great-Falls-Tool-Bus/.github.git "$scratch/mirror"
    git -C "$scratch/mirror" checkout --quiet HEAD -- githooks
    git -c core.filemode=true diff --no-index --exit-code -- "$scratch/mirror/githooks" .githooks

hooks-test:
    bash .githooks/test.sh
