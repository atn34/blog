---
title:  "twitter fortune"
date:   2014-04-04
categories: [bash,twitter,lilb]
---

# Motivation #

Recently, my friend [Ben Carriel](https://twitter.com/BkcMath) decided
he wanted a random [lil b](https://twitter.com/LILBTHEBASEDGOD) tweet
to appear in his emacs start buffer. I liked the idea.
I set out to make it happen for my vim start screen.

# Fortune #

Linux comes with the [`fortune`](http://linux.die.net/man/6/fortune)
utility, which serves a similar purpose: when run with no arguments
it prints a "random, hopefully interesting, adage". For example,

```{.terminal  .notest}
$ fortune
You are only young once, but you can stay immature indefinitely.
```

Fortune reads these adages from fortune files. I thought it'd be nice
to have a script that can generate fortune files from a twitter
user's tweets.

# Twitter #

I found a nice tool made by Kai Hendry called [greptweet](http://greptweet.com/)
that can request up to 3000 tweets, with a nice webapi.

To use it, first fetch the tweets

```{.terminal .notest}
$ curl -s http://greptweet.com/f/$TWITTER_HANDLE > /dev/null
```

When that's done, you can download the tweets like so

```{.terminal .notest}
$ curl -s http://greptweet.com/u/lilbthebasedgod/tweets.txt | head -1
451980332581928960|Fri Apr 04 07:11:23 +0000 2014|Smile for me, I love you - Lil B
```

To use the tweets with fortune,
we need to format the tweets the way `fortune` wants:

```{.terminal .notest}
$ curl -s http://greptweet.com/u/$TWITTER_HANDLE/tweets.txt \
    | cut -f3 -d'|' \
    | grep -v '\<RT\>\|\<http\|@' \
    | awk "1; { print \"\t\t-- @$TWITTER_HANDLE\n%\"; }"
```

`cut -f3 -d'|'` to keep field 3 where fields are delimited by '|',
`grep -v '\<RT\>\|\<http\|@'` to filter out the retweets, tweets with links,
and tweets with `@` mentions, and
`awk "1; { print \"\t\t-- @$TWITTER_HANDLE\n%\"; }"` to format the tweets.
I got the awk one-liner [here](http://www.theunixschool.com/2012/08/insert-new-line-after-every-n-lines.html).
Basically `1` (true) prints every line by default,
then we print who the tweet is by, and `%` on its own line to delimit
the strings for `fortune`.

Full script available [here](https://github.com/atn34/twitter-fortune). There
were some stray html entities in the tweets (eg `&amp;` or `&lt;` or `&gt;`),
so I threw some `sed` in the pipeline to clean those up.

One more complication: before `fortune` can use the file, we need
to use [`strfile`](http://linux.die.net/man/1/strfile) to allow for
random access of strings in the file.

```{.terminal .notest}
$ ./twitter-fortune.sh lilbthebasedgod > fortune-file
$ strfile fortune-file
$ fortune fortune-file
Love you and i love life !!!!! Thank you for waking up today - Lil B
                -- @lilbthebasedgod
```

Then you'll probably want to add your new fortune file to the rest of them.
Use `$ fortune -f` to see where the rest of your fortune files are.

# Vim #

I used Marco Hinz's [vim startify](https://github.com/mhinz/vim-startify)
for my custom vim start screen.

Once installed, I added the following bit of configuration to use
`fortune` as my custom header

```
let g:startify_custom_header =
    \ map(split(system('fortune'), '\n'), '"   ". v:val') + ['','']
```

# Final Result #

![Final result](http://i.imgur.com/MKYrQeO.png?1?8351)
