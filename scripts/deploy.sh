#!/usr/bin/env bash
# Deploy the built site to the docs host as a new release and switch the "current" symlink.
#   scripts/deploy.sh            build/ -> releases/<timestamp>, then current -> that release
#   scripts/deploy.sh rollback   current -> the previous release (the one before the current target)
#   scripts/deploy.sh list       show releases and where current points
# Env: DOCS_SSH (default root@2.25.68.244), DOCS_SSH_KEY (private key path), DOCS_ROOT (default /var/www/erdilrf-docs)
# Needs the nginx block that serves /docs/ from $DOCS_ROOT/current/docs/ (see README).
set -euo pipefail
HOST="${DOCS_SSH:-root@2.25.68.244}"
KEY="${DOCS_SSH_KEY:-$HOME/.ssh/erdilrf_ed25519}"
ROOT="${DOCS_ROOT:-/var/www/erdilrf-docs}"
SSH=(ssh -i "$KEY" -o ConnectTimeout=15 -o BatchMode=yes "$HOST")

case "${1:-deploy}" in
  list)
    timeout 60 "${SSH[@]}" "ls -1 $ROOT/releases; echo current = \$(readlink $ROOT/current)"
    ;;
  rollback)
    timeout 60 "${SSH[@]}" "set -e; cur=\$(basename \$(readlink $ROOT/current)); prev=\$(ls -1 $ROOT/releases | grep -B1 -x \$cur | head -1); [ \"\$prev\" != \"\$cur\" ] || { echo no earlier release; exit 1; }; ln -sfn $ROOT/releases/\$prev $ROOT/current; echo current = \$prev"
    ;;
  deploy)
    [ -d build ] || { echo "run npm run build first"; exit 1; }
    TS=$(date +%Y%m%d-%H%M%S)
    STAGE=$(mktemp -d)
    cp -r build "$STAGE/docs"
    tar -czf - -C "$STAGE" docs | timeout 300 "${SSH[@]}" "mkdir -p $ROOT/releases/$TS && tar -xzf - -C $ROOT/releases/$TS && chown -R root:root $ROOT/releases/$TS && find $ROOT/releases/$TS -type d -exec chmod 755 {} + && find $ROOT/releases/$TS -type f -exec chmod 644 {} +"
    timeout 60 "${SSH[@]}" "ln -sfn $ROOT/releases/$TS $ROOT/current; echo \"current = $TS\""
    rm -rf "$STAGE"
    ;;
esac
