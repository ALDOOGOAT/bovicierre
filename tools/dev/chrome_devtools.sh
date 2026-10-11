#!/bin/sh
# XAUTHORITY cambia al iniciar sesión; usar la sesión gráfica actual.
set -eu
export PATH="$HOME/.nvm/versions/node/v24.21.0/bin:$PATH"
export DISPLAY="${DISPLAY:-:0}"
if [ -z "${XAUTHORITY:-}" ]; then
    XAUTHORITY=$(ps -u "$(id -u)" -o args= | awk '/^\/usr\/bin\/Xwayland / { for (i=1; i<NF; i++) if ($i == "-auth") { print $(i+1); exit } }')
    export XAUTHORITY
fi
exec npx -y chrome-devtools-mcp@1.10.1 \
    --no-usage-statistics --no-performance-crux \
    --user-data-dir="$HOME/.local/share/bovicierre-tools/chrome-profile" "$@"
