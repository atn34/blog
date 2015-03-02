---
title:  Existence of Uncomputable Functions
date: 2015-03-02
categories: []
draft: true
base: post.html
---

In this post, we shall prove the existence of uncomputable functions.
Let's call a function *uncomputable* if there does not exist a finite program
which computes it, and let's restrict our attention to functions from the naturals to the set $\{0, 1\}$.
The most straightforward way to prove the existence of
something is to give an example of it. Yet if we could give a finite description
of such a function, we would immediately have a program which computes it!
We must use another technique.

We know we can enumerate
programs, as programs are a subset of strings, and we can enumerate strings as follows.

#. ""
#. "a"
#. "b"
#. $...$
#. "aa"
#. "ab"
#. $...$
#. "ba"
#. "bb"
#. $...$

Let's try enumerating functions. The $i$th row in represents the $i$th function.

|----------|----------|---------|-----|
| $f_0(0)$ | $f_0(1)$ |$f_0(2)$ |$...$|
| $f_1(0)$ | $f_1(1)$ |$f_1(2)$ |$...$|
| $f_2(0)$ | $f_2(1)$ |$f_2(2)$ |$...$|
| $...$    | $...$    |$...$    |$...$|

Consider the following function.

$$f(i) = \begin{cases} 0 & \mbox{if } f_i(i) = 1 \\ 1 & \mbox{if } f_i(i) = 0\end{cases}$$

Since $f$ differs from $f_i$ on the $i$th input, $f$ cannot be one of the functions enumerated.
We cannot enumerate functions $f : N \rightarrow \{0, 1\}$.

Since we cannot enumerate functions, but we can enumerate programs there exists a function
that has no program which computes it.
