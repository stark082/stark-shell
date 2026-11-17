#!/usr/bin/env bash
# Download a complete checkout before executing any installer code.
set -euo pipefail
fail() { printf 'stark-bootstrap: %s\n' "$*" >&2; exit 1; }
export GIT_TERMINAL_PROMPT=0
export GIT_ASKPASS=/bin/false
repo=https://github.com/stark082/stark-shell.git
ref=v0.1.0
commit=${STARK_COMMIT:-}
dev=false
args=()
while (($#)); do
    case "$1" in
        --ref|--commit|--dev-branch)
            (($# >= 2)) || fail "$1 requires a value"
            case "$1" in
                --ref) ref=$2 ;;
                --commit) commit=$2 ;;
                --dev-branch) ref=$2; dev=true ;;
            esac
            shift 2 ;;
        *) args+=("$1"); shift ;;
    esac
done
command -v git >/dev/null || fail 'git is required; install git with your package manager'
command -v python3 >/dev/null || fail 'Python 3.10+ is required'
[[ "$ref" != -* ]] || fail 'invalid Git reference'
if ! $dev; then
    [[ "$ref" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$ ]] || fail 'release reference must be a semantic version tag'
    [[ "$commit" =~ ^[0-9a-f]{40}$ ]] || fail 'release installation requires --commit FULL_SHA from independently reviewed release metadata; use --dev-branch main only for unverified development'
fi
stage=$(mktemp -d "${TMPDIR:-/tmp}/stark-bootstrap.XXXXXXXX")
trap 'rm -rf -- "$stage"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
git -c credential.helper= clone --depth 1 --branch "$ref" -- "$repo" "$stage/source" || fail 'download failed or reference does not exist; no installer executed'
actual=$(git -C "$stage/source" rev-parse HEAD)
if [[ -n "$commit" && "$actual" != "$commit" ]]; then
    fail "integrity mismatch: expected $commit, received $actual"
fi
if $dev; then printf '%s\n' 'WARNING: explicitly selected unverified development source.' >&2; fi
printf 'Source: %s (%s)\n' "$ref" "$actual"
bash "$stage/source/install.sh" "${args[@]}"
