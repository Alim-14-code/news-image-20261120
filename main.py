#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261120.

Copies the pre-rendered entry.png (built in this repository) to the
harness output directory. Standard library only, no network, no clock,
fully deterministic — both grading runs write byte-identical output.

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("copied entry.png ->", dst)


if __name__ == "__main__":
    sys.exit(main())
