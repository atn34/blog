---
title:  Git Hooks and Haskell Tags
date:   2014-04-09
categories: [git,haskell,vim,ctags]
---

# git hooks and tags #

I've been using Tim Pope's [effortless ctags with git](http://tbaggery.com/2011/08/08/effortless-ctags-with-git.html)
blog post to keep my tags file up to date. The gist of it is to keep your tags file in `.git/tags`
(if you have the excellent [vim-fugitive](https://github.com/tpope/vim-fugitive) installed vim is configured to look there)
and update your tags file whenever the working tree changes. This comes in two parts: a script to update `.git/tags`,
and hooks to call that script.

Following Tim Pope's advice, and the advice of some of his commenters, I ended up with a script to update the tags
that looked something like this:

```bash
#! /bin/sh

GITDIR=$(git rev-parse --git-dir)
TAGSFILE=tags.$$

mkdir $GITDIR/tags_lock 2>/dev/null || exit 0
trap "rmdir $GITDIR/tags_lock; rm $GITDIR/$TAGSFILE" EXIT

ctags --tag-relative -Rf $GITDIR/$TAGSFILE --exclude=$GITDIR

mv $GITDIR/$TAGSFILE $GITDIR/tags
```

This uses [exuberant ctags](http://ctags.sourceforge.net/) to generate the
tags file, and uses directory based locking[^1] so that a large rebase does not
start tons of processes.
`git rev-parse --git-dir` gets the git directory, and using it makes this work with submodules[^2].

[^1]: Thanks [Rich Healy](http://tbaggery.com/2011/08/08/effortless-ctags-with-git.html#comment-728214764).
[^2]: Thanks [Paul](http://tbaggery.com/2011/08/08/effortless-ctags-with-git.html#comment-837431209).

# generating haskell tags #

This works great for the [languages](http://ctags.sourceforge.net/languages.html)
that exuberant ctags supports, but unfortunately haskell is not one of those languages.
This means we need to add in support for haskell tags.

The haskell wiki [lists](http://www.haskell.org/haskellwiki/Tags) some possible solutions.

- [GHCi](http://www.haskell.org/haskellwiki/GHC/GHCi) can generate tags files. But to generate the tags, GHCi needs to know what language extensions to use and what modules to load. This information might be stored in a cabal file or a `.ghci` file, but we can't rely on that.
- [gasbag](http://kingfisher.nfshost.com/sw/gasbag/) does not understand all Haskell extensions, and cannot index haskell files that don't compile.
- [hothasktags](http://hackage.haskell.org/package/hothasktags) hothasktags needs to know language extensions (like GHCi), and cannot index haskell files that don't compile (like gasbag).
- [hasktags](http://hackage.haskell.org/package/hasktags) uses its own parser and therefore does not care about language extensions or valid Haskell. Hasktags does have some problems (see [this](http://stackoverflow.com/questions/10058411/how-to-generate-tags-for-haskell-projects) stack overflow post), but I went with it.
- [fast-tags](http://hackage.haskell.org/package/fast-tags) Fast-tags addresses some of the problems with hasktags in the above stack overflow post, but it's under-documented and I have yet to run into hasktags' issues anyway.

# combining hasktags and ctags #

We could simply append the tags produced by hasktags to the tags from ctags,
but vim expects tags files to be sorted (so it can [binary search](http://en.wikipedia.org/wiki/Binary_search_algorithm) them). We must append then [sort](http://linux.die.net/man/1/sort)
(using `LC_COLLATE=C` as advised [here](http://vim.wikia.com/wiki/Arbitrary_tags_for_file_names)).

```bash
# exuberant ctags
ctags --tag-relative -Rf $GITDIR/$TAGSFILE --exclude=$GITDIR

# hasktags
if which hasktags > /dev/null ; then
    OLD_DIR=$(pwd)
    (cd $GITDIR && hasktags -c -x --ignore-close-implementation -a -f $TAGSFILE $OLD_DIR)
    LC_COLLATE=C sort $GITDIR/$TAGSFILE -o $GITDIR/$TAGSFILE
fi
```

Explanation of hasktags options:

- `-c` means generate a vim (not emacs) format tags file,
- `-x` means generate additional information,
- `--ignore-close-implementation` avoids tagging both type signatures and implementations if the implementation is near the type signature.
- `-a` means append
- `-f` specifies output file

Full script available as a [gist](https://gist.github.com/10231136)
