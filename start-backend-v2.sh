#!/bin/bash

# Start the FastAPI backend with timing tracking
cd "$(dirname "$0")"
source venv/bin/activate
python -m uvicorn api.main_v2:app --host 0.0.0.0 --port 8000 --reload

