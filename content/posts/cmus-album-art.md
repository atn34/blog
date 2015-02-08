---
title:  "cmus album art"
date:   2014-04-05
categories: [bash,cmus,beets,music]
---

# cmus #

I've been using [cmus](https://cmus.github.io/) as my music player
for a while now. It's small, fast, and simple with vim-like keybindings,
and you can configure it to run an external script to display
status changes. I wrote a script to change my desktop background to the album art
of whatever song is currently playing.

# beets #

This only works with a well organized music library with art
for every album. I use [beets](http://beets.radbox.org/). Beets
organizes a music library so that every album's directory follows this format:
`/path/to/music/albumartist/album/`. With the help of some plugins,
it can also fetch album art, embed it in `.mp3`'s, and save it as
`cover.jpg` in the album's directory. I've [configured](http://beets.readthedocs.org/en/v1.3.3/reference/config.html) beets to resize album art to a max width
of 500 for consistency. Most album art seems to be 500x500 anyway.

Here is my `config.yaml`

```
directory: /home/andrew/music
library: /home/andrew/music/library.blb
plugins: fetchart missing embedart
fetchart:
    maxwidth: 500
```


# cmus notify script #

cmus calls your status display script with a series of key-value pairs
as arguments. I started with [this script](https://github.com/nblock/cmus-notify/blob/master/cmus-notify), and added some functionality to set the background.

We need the filepath of the album art. For that we need the album artist
and album title. The album title is easy: it's passed in as one
of the key value pairs. The album artist is not. We can, however, get it
using `cmus-remote`.

```bash
ALBUMARTIST=$(cmus-remote -Q | grep -w albumartist | cut -d" " -f 3- | sanitize_path)
```

`cmus-remote -Q` to
["Get player status information"](http://linux.die.net/man/1/cmus-remote),
`grep -w albumartist` picks out the line with the album artist,
and `cut -d" " -f 3-` to keep the 3rd field to the end of the line, where
fields are delimited by a space. As for `sanitize_path`, beets translates some
characters to underscores when creating directories,
so we'll use a `sed` pipeline to follow suit.

```bash
sanitize_path() {
    sed 's/\.$/_/g' \
    | sed 's@/@_@g' \
    | sed 's/:/_/g' \
    | sed 's/Various Artists/Compilations/g' \
    | sed 's/\?/_/g' \
    | sed 's/\*/_/g'
}
```

Finally, we have the path

```bash
ALBUM=$(echo "$_album" | sanitize_path)
PATH="$HOME/music/$ALBUMARTIST/$ALBUM/cover.jpg"
```

We can use [feh](https://github.com/derf/feh) or similar
to set the background

```bash
feh --bg-center --save "$PATH"
```

Full script available as a [gist](https://gist.github.com/9996000)

To install, run `:set status_display_program=/path/to/cmus-notify.sh`
inside cmus.
