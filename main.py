#!/usr/bin/env python3
"""Write the entry image to the output directory.

The front page is drawn by gen.py and committed as entry.png; the grader runs
this program with no network, so all it has to do is copy those exact bytes.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"), os.path.join(OUT, "entry.png"))
print("wrote", os.path.join(OUT, "entry.png"))
