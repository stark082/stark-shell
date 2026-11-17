#!/usr/bin/env bash
# User-scoped local entry point. Only missing package installation uses sudo.
set -euo pipefail
STARK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if (( EUID == 0 )); then
    printf '%s\n' 'Run ./install.sh as your normal desktop user, without sudo.' >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    dry=false
    consent=false
    install_deps=false
    for arg in "$@"; do
        case "$arg" in
            --dry-run|--help|-h) dry=true ;;
            --install-deps) install_deps=true ;;
            --yes) consent=true ;;
        esac
    done
    printf '%s\n' 'Missing Python 3.10+. Required package command: sudo pacman -S --needed python' >&2
    if $dry; then
        printf '%s\n' 'Preview only: no packages or desktop files changed; validation needs Python.' >&2
        exit 1
    fi
    if ! command -v omarchy >/dev/null || ! command -v pacman >/dev/null; then
        printf '%s\n' 'Install/repair supported Omarchy before running Stark Shell.' >&2
        exit 1
    fi
    if [[ -t 0 ]] && ! $consent; then
        read -r -p 'Install Python using sudo pacman? [y/N] ' answer
        [[ "$answer" == y || "$answer" == Y ]] || exit 1
        sudo pacman -S --needed python
    elif $install_deps && $consent; then
        sudo pacman -S --needed --noconfirm python
    else
        printf '%s\n' 'For automation, authorize packages with --install-deps --yes, or install Python yourself.' >&2
        exit 1
    fi
fi
# No-argument terminal use starts the beginner wizard. Automation stays minimal.
if (( $# == 0 )) && [[ -t 0 ]]; then
    set -- --interactive
fi
exec python3 "$STARK_ROOT/tools/stark_manager.py" install "$@"
