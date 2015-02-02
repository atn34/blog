#!/bin/sh

make site
cd site
python -m SimpleHTTPServer &
PID=$!
trap "kill $PID" EXIT
linkchecker http://0.0.0.0:8000/
