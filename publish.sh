#!/bin/bash
# Build the site and put it LIVE on copperpos.uz.
cd "$(dirname "$0")" || exit 1
node build.mjs || exit 1
read -r -p "Publish to copperpos.uz now? (y/n) " ok
[ "$ok" = "y" ] || { echo "Cancelled."; exit 0; }
npx --yes wrangler@latest pages deploy dist --project-name copper-site --branch main
