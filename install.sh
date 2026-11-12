#!/usr/bin/env bash
# Installs (or removes) the bridge and the Steam launch wrapper into ~/.local/bin.
#   ./install.sh            install
#   ./install.sh --uninstall
set -euo pipefail

PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="${PREFIX}/bin"
SRC_DIR="$(cd -- "$(dirname -- "$0")" && pwd)/bin"
FILES=(rdr2-dualsense-native rdr2-with-triggers)

if [ "${1:-}" = "--uninstall" ]; then
    for f in "${FILES[@]}"; do
        rm -fv "${BIN_DIR}/${f}"
    done
    exit 0
fi

command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' \
    || { echo "python3 >= 3.9 is required" >&2; exit 1; }

mkdir -p "$BIN_DIR"
for f in "${FILES[@]}"; do
    install -m 0755 "${SRC_DIR}/${f}" "${BIN_DIR}/${f}"
    echo "installed ${BIN_DIR}/${f}"
done

cat <<EOF

Done. In Steam, set the launch options of Red Dead Redemption 2 to:

    WINEDLLOVERRIDES="dinput8=n,b" ${BIN_DIR}/rdr2-with-triggers %command%
EOF
