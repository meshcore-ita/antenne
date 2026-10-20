#!/bin/sh
#
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python3 tools/build.py      # scrive site/
python3 -m http.server -d site

# git add .
# git commit -m "commit_all"
# git push -u origin main
