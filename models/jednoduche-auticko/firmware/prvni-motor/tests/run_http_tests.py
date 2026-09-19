#!/usr/bin/env python3
"""Compile the real sketch against host-only mocks; never access hardware."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--browser', action='store_true', help='Also run real Chromium HTTP integration (requires Playwright).')
parser.add_argument('--source', type=Path, default=HERE.parent / 'prvni-motor.ino')
args = parser.parse_args()
source = args.source.resolve()
line, total, deadline = 1024, 8192, 3000
print('Sketch:', source, flush=True)
print('SHA256:', hashlib.sha256(source.read_bytes()).hexdigest(), flush=True)
with tempfile.TemporaryDirectory(prefix='first-motor-http-tests-') as directory:
    binary = Path(directory) / 'http-tests'
    command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-I', str(HERE),
               f'-DSKETCH_PATH="{source}"', f'-DTEST_MAX_LINE={line}',
               f'-DTEST_MAX_BYTES={total}', f'-DTEST_DEADLINE={deadline}',
               str(HERE / 'http_tests.cpp'), '-o', str(binary)]
    subprocess.run(command, check=True)
    subprocess.run([str(binary)], check=True)

subprocess.run(['node', str(HERE / 'browser_tests.js'), str(source)], check=True)

if args.browser:
    subprocess.run(['node', str(HERE / 'browser_http_tests.js'), str(source)], check=True)
