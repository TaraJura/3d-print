#!/usr/bin/env python3
"""Compile the real sketch against host-only mocks; never access hardware."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=HERE.parent / 'prvni-motor.ino')
parser.add_argument('--legacy', action='store_true', help='Reproduce the original 128/1024/1000 limits.')
args = parser.parse_args()
source = args.source.resolve()
line, total, deadline = (128, 1024, 1000) if args.legacy else (1024, 8192, 3000)
print('Sketch:', source, flush=True)
print('SHA256:', hashlib.sha256(source.read_bytes()).hexdigest(), flush=True)
with tempfile.TemporaryDirectory(prefix='first-motor-http-tests-') as directory:
    binary = Path(directory) / 'http-tests'
    command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-I', str(HERE),
               f'-DSKETCH_PATH="{source}"', f'-DTEST_MAX_LINE={line}',
               f'-DTEST_MAX_BYTES={total}', f'-DTEST_DEADLINE={deadline}',
               f'-DEXPECT_MOBILE_REJECTED={int(args.legacy)}',
               str(HERE / 'http_tests.cpp'), '-o', str(binary)]
    subprocess.run(command, check=True)
    subprocess.run([str(binary)], check=True)
