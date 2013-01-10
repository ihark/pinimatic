#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if 'PYTHONHOME' in os.environ:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pinry.settings.production")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pinry.settings.development")
    
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
