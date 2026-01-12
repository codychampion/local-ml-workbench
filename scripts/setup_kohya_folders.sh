#!/bin/bash
# Automated Kohya Folder Setup Script
# Renames folders to match Kohya's N_concept naming convention

set -e

DATA_DIR="./data"
FALLOUT_DIR="${DATA_DIR}/fallout"

echo "=== Kohya Folder Setup ==="
echo "Checking for folders to rename..."

# Function to rename folder if it exists
rename_if_exists() {
    local old_name="$1"
    local new_name="$2"

    if [ -d "${FALLOUT_DIR}/${old_name}" ]; then
        echo "  Renaming: ${old_name} -> ${new_name}"
        mv "${FALLOUT_DIR}/${old_name}" "${FALLOUT_DIR}/${new_name}"
    fi
}

# Create fallout directory if it doesn't exist
mkdir -p "${FALLOUT_DIR}"

# Rename folders to Kohya format (case-insensitive checks)
for dir in "${FALLOUT_DIR}"/*; do
    if [ -d "$dir" ]; then
        basename=$(basename "$dir")
        case "${basename,,}" in
            "fallout")
                [ "$basename" != "10_fallout" ] && rename_if_exists "$basename" "10_fallout"
                ;;
            "fnv"|"newvegas"|"new_vegas")
                [ "$basename" != "10_newvegas" ] && rename_if_exists "$basename" "10_newvegas"
                ;;
            "fo4"|"fallout4"|"fallout_4")
                [ "$basename" != "10_fallout4" ] && rename_if_exists "$basename" "10_fallout4"
                ;;
            "fo76"|"fallout76"|"fallout_76")
                [ "$basename" != "10_fallout76" ] && rename_if_exists "$basename" "10_fallout76"
                ;;
        esac
    fi
done

# Create missing folders
echo ""
echo "Ensuring all training folders exist..."
mkdir -p "${FALLOUT_DIR}/10_fallout"
mkdir -p "${FALLOUT_DIR}/10_newvegas"
mkdir -p "${FALLOUT_DIR}/10_fallout4"
mkdir -p "${FALLOUT_DIR}/10_fallout76"

# Count images in each folder
echo ""
echo "=== Training Data Summary ==="
for folder in "${FALLOUT_DIR}"/10_*; do
    if [ -d "$folder" ]; then
        count=$(find "$folder" -type f \( -iname "*.jpg" -o -iname "*.png" -o -iname "*.jpeg" -o -iname "*.webp" \) 2>/dev/null | wc -l)
        echo "  $(basename $folder): ${count} images"
    fi
done

echo ""
echo "✓ Folder setup complete!"
echo "  Training path for Kohya GUI: /app/data/fallout"
