"""
WSGI config for dc_master project.
Handles Vercel cold-start: copies pre-seeded SQLite DB to /tmp and runs migrations.
"""

import os
import shutil

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dc_master.settings")

# ── Vercel cold-start bootstrap ────────────────────────────────────────────────
if os.environ.get('VERCEL') == '1':
    tmp_db = '/tmp/db.sqlite3'
    flag_file = '/tmp/.db_ready'

    if not os.path.exists(flag_file):
        # Get the source DB shipped with the project (pre-seeded)
        from pathlib import Path
        source_db = Path(__file__).resolve().parent.parent / 'db.sqlite3'

        if source_db.exists():
            shutil.copy2(str(source_db), tmp_db)

        # Run any pending migrations
        from django.core.management import call_command
        import django
        django.setup()
        try:
            call_command('migrate', '--run-syncdb', verbosity=0)
        except Exception:
            pass

        # Seed only if no users exist yet
        try:
            from accounts.models import CustomUser
            if not CustomUser.objects.exists():
                call_command('seed_data', verbosity=0)
        except Exception:
            pass

        # Mark DB as ready so next request in same container skips this
        with open(flag_file, 'w') as f:
            f.write('1')

# ── WSGI app ───────────────────────────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
