#!/usr/bin/env python3

import os
import subprocess
import sys

if not os.environ.get('DESTDIR'):
    print('Compiling GSettings schemas...')
    schema_dir = os.path.join(sys.argv[1], 'share', 'glib-2.0', 'schemas')
    subprocess.call(['glib-compile-schemas', schema_dir])
