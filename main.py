import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "entry.png")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    os.makedirs(OUT, exist_ok=True)
    target = os.path.join(OUT, "entry.png")
    shutil.copyfile(SRC, target)
    print("copied entry.png -> " + target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
