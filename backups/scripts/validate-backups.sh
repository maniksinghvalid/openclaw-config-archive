#!/bin/bash
# Simple validation checking for core files
REQUIRED_FILES=("MEMORY.md" "SOUL.md" "TOOLS.md")
MISSING=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ] && [ ! -f "backups/$file" ]; then
        echo "⚠️  Warning: $file missing from backup set"
        MISSING=1
    fi
done
if [ $MISSING -eq 0 ]; then
    echo "✅ Backup validation passed: Core files present."
else
    echo "⚠️  Backup validation finished with warnings."
    exit 1
fi
