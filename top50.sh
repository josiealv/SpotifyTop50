#!/bin/bash

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
python3 main.py