#!/bin/bash
# Build the site and open it on this Mac (nothing goes online).
cd "$(dirname "$0")" || exit 1
node build.mjs || exit 1
pkill -f "http.server 8765" 2>/dev/null
(cd dist && python3 -m http.server 8765 >/dev/null 2>&1 &)
sleep 1
open "http://localhost:8765/"
echo "Preview open at http://localhost:8765/  (RU: /ru/  EN: /en/)"
