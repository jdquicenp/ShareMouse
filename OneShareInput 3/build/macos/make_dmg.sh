#!/usr/bin/env bash
set -euo pipefail
APP="OneShareInput.app"
VOL="OneShareInput"
DMG="OneShareInput-0.1.0.dmg"
DIST="dist"
if [ ! -d "$DIST/$APP" ]; then
  echo "No existe $DIST/$APP. Ejecuta build_app.sh primero."
  exit 1
fi

TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/$VOL"
cp -R "$DIST/$APP" "$TMPDIR/$VOL/"
# Crear .dmg con hdiutil (macOS built-in)
hdiutil create -volname "$VOL" -srcfolder "$TMPDIR/$VOL" -ov -format UDZO "$DIST/$DMG"
echo "DMG listo: $DIST/$DMG"
