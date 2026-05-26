"""
WSGI config for dc_master project.
On Vercel cold-start: copies the pre-seeded SQLite DB from the project bundle
to /tmp (the only writable location), then auto-migrates and seeds if needed.
"""

import os
import shutil
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dc_master.settings")

# ── Vercel cold-start bootstrap ────────────────────────────────────────────────
if os.environ.get('VERCEL') == '1':
    tmp_db   = '/tmp/db.sqlite3'
    flag     = '/tmp/.db_ready'

    if not os.path.exists(flag):
        # Copy the pre-seeded DB bundled with the project
        source_db = Path(__file__).resolve().parent.parent / 'db.sqlite3'
        if source_db.exists() and not os.path.exists(tmp_db):
            shutil.copy2(str(source_db), tmp_db)

        # Mark ready — subsequent warm requests skip bootstrap
        with open(flag, 'w') as f:
            f.write('1')

# ── WSGI application ───────────────────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
app = application
