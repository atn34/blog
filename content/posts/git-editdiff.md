---
layout: post
title:  "git editdiff"
date:   2014-10-21
categories: [git,bash,vim]
draft: true
---

# Motivation #

I often use `git diff` to view what I've done since last commiting. If I like it, I'll commit it. If I don't like it, I'll go back and work to fix it. But for something simple like a typo, going off to make the fix in the working tree seems like overkill.

# git editdiff #

TODO

- git-editdiff script
- vim-editdiff plugin
    - [c ]c motions
    - treat -, + in beginning of line as if they weren't there
        - {, } mappings
        - J command
        - o, O add + or - automatically
    - automatic rediff on save
