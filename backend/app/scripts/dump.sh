#!/bin/bash

REPO_DIR="${1:-.}"
shift

IGNORE_DIRS=("node_modules" "dev-dist")
while [[ $# -gt 0 ]]
do
    IGNORE_DIRS+=("$1")
    shift
done

OUTPUT_FILE="combined_code_dump.txt"

FILE_EXTENSIONS=("py" "ts" "typed" "tsx")

> "$OUTPUT_FILE"

combine_files() {
  local dir="$1"
  for ext in "${FILE_EXTENSIONS[@]}"
  do
    find "$dir" -type f -name "*.$ext" -print0 | while IFS= read -r -d '' file
    do
      ignore_file=false
      for ignore_dir in "${IGNORE_DIRS[@]}"
      do
        if [[ "$file" == *"/$ignore_dir/"* ]]
        then
          ignore_file=true
          break
        fi
      done
      if [ "$ignore_file" = false ]
      then
        echo "// File: $file" >> "$OUTPUT_FILE"
        cat "$file" >> "$OUTPUT_FILE"
        echo -e "\n\n" >> "$OUTPUT_FILE"
      fi
    done
  done
}

combine_files "$REPO_DIR"

echo "All code files have been combined into $OUTPUT_FILE"
