#!/usr/bin/env bash
set -e
python3 -m py_compile "$(dirname "$0")/../ai_doctor.py"
python3 "$(dirname "$0")/../ai_doctor.py" --version | grep -q "ai-doctor" && echo "smoke passed"
