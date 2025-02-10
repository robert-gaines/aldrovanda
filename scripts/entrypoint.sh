#!/bin/bash
service smbd start
source /app/venv/bin/activate
gunicorn -w 4 --preload -b 0.0.0.0:80 app:app &
python /app/scheduler.py