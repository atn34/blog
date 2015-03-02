#! /bin/sh

REV=HEAD

SHA=$(git rev-list $REV | head -1)

DEPLOYDIR=/tmp/blog-deploy-$SHA
SOURCEDIR=/tmp/blog-source-$SHA

DEPLOYREMOTE=git@github.com:atn34/atn34.github.io.git
GITHUBSRC=atn34/blog

trap "rm -rf $DEPLOYDIR $SOURCEDIR" EXIT

mkdir $DEPLOYDIR
mkdir $SOURCEDIR

git clone $DEPLOYREMOTE $DEPLOYDIR
(cd $DEPLOYDIR && git ls-files | xargs rm -f)

git archive --format=tar $REV | (cd $SOURCEDIR && tar xf -)

./render.py build --dest $DEPLOYDIR --source $SOURCEDIR/content || exit

(cd $DEPLOYDIR && \
    git add . && \
    git commit -m "build of $GITHUBSRC@$SHA" && \
    git push origin master)
