#!/usr/bin/env bash
# Bootstrapt einen neuen Eigen-Service aus dem Template.
#
# Usage:
#   ./scripts/new-service.sh <service-name> <port>
#
# Beispiel:
#   ./scripts/new-service.sh finanzen 8111

set -euo pipefail

NAME="${1:-}"
PORT="${2:-}"

if [[ -z "$NAME" || -z "$PORT" ]]; then
    echo "Usage: $0 <service-name> <port>" >&2
    exit 1
fi

if [[ ! "$NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
    echo "service-name muss kebab-case sein (^[a-z][a-z0-9-]*$)" >&2
    exit 1
fi

TEMPLATE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PARENT_DIR="$(dirname "$TEMPLATE_DIR")"
TARGET="${PARENT_DIR}/${NAME}"

if [[ -e "$TARGET" ]]; then
    echo "Zielverzeichnis existiert bereits: $TARGET" >&2
    exit 1
fi

echo "==> Kopiere Template nach $TARGET"
cp -r "$TEMPLATE_DIR" "$TARGET"
rm -rf "$TARGET/.git" "$TARGET/scripts/new-service.sh"

echo "==> Ersetze Platzhalter"
# service-name in compose + nginx snippets
sed -i "s|my-service|${NAME}|g" "$TARGET/docker-compose.service-fragment.yml"
sed -i "s|my-service|${NAME}|g" "$TARGET/nginx.service-fragment.conf"
sed -i "s|81XX|${PORT}|g" "$TARGET/docker-compose.service-fragment.yml"

# service_name default in config
sed -i "s|service-template|${NAME}|g" "$TARGET/app/config.py"
sed -i "s|service-template|${NAME}|g" "$TARGET/pyproject.toml"

echo ""
echo "Fertig. Nächste Schritte:"
echo "  1. cd $TARGET"
echo "  2. docker-compose.yml anpassen (build:. → service + network)"
echo "  3. In /home/user/docker/docker-compose.yml aufnehmen"
echo "  4. nginx.service-fragment.conf in dev-portal/nginx.conf einfügen"
echo "  5. docker compose up -d --build"
