from pathlib import Path
import sys
import time

OUTPUT_DIR = Path("app/output")
log_file = OUTPUT_DIR / "healthcheck.log"
summary = OUTPUT_DIR / "summary_report.txt"

if not log_file.exists():
    sys.exit(1)
elif not summary.exists():
    sys.exit(1)

last_modified = log_file.stat().st_mtime
if time.time() - last_modified > 120:
    sys.exit(1)

sys.exit(0)
