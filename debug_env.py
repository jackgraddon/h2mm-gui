#!/usr/bin/env python3

import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"XDG_DATA_DIRS: {os.environ.get('XDG_DATA_DIRS', 'Not set')}")
print(f"GSETTINGS_SCHEMA_DIR: {os.environ.get('GSETTINGS_SCHEMA_DIR', 'Not set')}")

try:
    import gi
    print(f"PyGObject (gi) found at: {gi.__file__}")
except ImportError:
    print("PyGObject (gi) not found!")

# Test for specific GTK components
try:
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    print(f"Gtk version: {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}")
except Exception as e:
    print(f"Error loading Gtk: {e}")
