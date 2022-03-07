#!/usr/bin/python
"""
    Copies stdin to stdout (screen) *and* the specified file.
"""
import fileinput
import os
from pathlib import Path
import sys

SHOW_FULL_PATH = False
DIVIDER = True
DIV_CH = ' '

if len(sys.argv) != 2:
    raise SystemExit('Usage: mytee <filepath>')

try:
    inp = fileinput.input(())  # Read from stdin.
    path = Path(sys.argv[1])
    stdout_write = sys.stdout.write
    stdout_flush = sys.stdout.flush
    # Assumes .py in same dir as output file.
    script = (f'{path.parent/path.stem}{path.suffix}' if SHOW_FULL_PATH else
              f'{path.stem}{path.suffix}')

    with open(path, 'w') as outp:  # Write to specified file.
        outp_write = outp.write
        outp_flush = outp.flush

        def write(line):
            stdout_write(line)
            outp_write(line)

        def writeln(line):
            write(line + '\n')

        banner = f'"{script}"' if ' ' in script else f'-[{script}]-'
        writeln(f'{banner}')
        if DIVIDER:
            writeln(f'{DIV_CH * len(banner)}')
        for line in inp:
            write(line)
        if DIVIDER:
            writeln(f'{DIV_CH * len(banner)}')
        writeln('-[done]-')
finally:
    inp.close()  # Not sure this is really necessary.

sys.exit(0)