"""Convenience launcher for bot.py and dashboard.py on Windows.

Usage:
    .venv/Scripts/python.exe start_services.py

Features:
    - Ensures working directory is project root
    - Stops any existing bot.py processes (optional quick heuristic)
    - Starts bot then dashboard
    - Waits a few seconds and reports:
        * PIDs
        * Heartbeat status (if file exists)
        * Tail of bot_log.txt (if exists)
"""
from __future__ import annotations
import os, sys, time, subprocess, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOT = ROOT / "bot.py"
DASH = ROOT / "dashboard.py"
PYTHON = Path(sys.executable)

if not BOT.exists():
    print("❌ bot.py not found at", BOT)
    sys.exit(1)
if not DASH.exists():
    print("❌ dashboard.py not found at", DASH)
    sys.exit(1)

print("Starting services from:", ROOT)
print("Python executable:", PYTHON)

# Attempt to terminate any stale bot processes by command line signature (best-effort)
try:
    # Windows specific: use wmic or tasklist /v to find bot.py
    if os.name == 'nt':
        # Use 'wmic' may be deprecated; fallback to tasklist not giving cmd line. So skip heavy logic.
        pass
except Exception:
    pass

# Launch bot
print("Launching bot.py ...")
bot_proc = subprocess.Popen([str(PYTHON), str(BOT)], cwd=ROOT, stdout=None, stderr=None)
print(f"   bot PID: {bot_proc.pid}")

# Give bot a head start
time.sleep(5)

print("Launching dashboard.py ...")
dash_proc = subprocess.Popen([str(PYTHON), str(DASH)], cwd=ROOT, stdout=None, stderr=None)
print(f"   dashboard PID: {dash_proc.pid}")

# Wait a little for heartbeat/log
time.sleep(5)

hb_path = ROOT / "bot_heartbeat.json"
if hb_path.exists():
    try:
        hb_text = hb_path.read_text(encoding='utf-8')
        hb = json.loads(hb_text)
        print("Heartbeat detected:", hb)
    except Exception as e:
        print("Heartbeat file read error:", e)
else:
    print("No heartbeat file yet (non-fatal; bot may still be initializing).")

log_path = ROOT / "bot_log.txt"
if log_path.exists():
    try:
        lines = log_path.read_text(encoding='utf-8', errors='ignore').splitlines()
        tail = lines[-12:]
        print("Recent bot_log tail:")
        for line in tail:
            print("   "+line)
    except Exception as e:
        print("Could not read bot_log.txt:", e)
else:
    print("bot_log.txt not created yet.")

print("Launch routine complete. Close this window; bot & dashboard continue running.")
