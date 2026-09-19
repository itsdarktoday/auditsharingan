#!/usr/bin/env python3
"""Compatibility entry point for older integrations.

New integrations should invoke ``scripts/auditsharingan.py`` directly. The
legacy filename remains only so existing automation fails forward into the
auditable engine instead of silently using the old best-effort runner.
"""

from auditsharingan import main


if __name__ == "__main__":
    raise SystemExit(main())
