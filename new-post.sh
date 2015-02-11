#! /bin/sh

usage() {
    echo "usage: $0 <title>"
}

if [ $# -eq 0 ] ; then
    usage
    exit 1
fi

TITLE="$@"
DATE=$(date +"%Y-%m-%d")

OUTPUTDIR="content/posts"

OUTFILE="$OUTPUTDIR/$(echo $TITLE | sed 's/ /-/g').md"

cat > "$OUTFILE" << EOF
---
title:  $TITLE
date:   $DATE
categories: []
draft: true
base: post.html
---

EOF

exec $EDITOR "$OUTFILE"
