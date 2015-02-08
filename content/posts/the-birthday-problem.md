---
title: "The Birthday Problem"
date: 2015-02-07
---

# The Birthday Problem #

Suppose there are $n$ people in a room, in a world with $k$ days in a year.
What's the probability that two people share a birthday? Assume that birthdays
are uniformly distributed throughout the year.

Let's start with some small examples. $P(1) = 0$, as there aren't even two
people.
When $n = 2$, if the first person's birthday is the $i$th day of the year, then
the second person's birthday must be the $i$th day as well. Then $P(2) = 1/k$.
When $n = 3$, it gets more complicated. If the first two people
share a birthday (probability $1/k$), then the probability is 1. If not, then
let person one have birthday on day $i$ and person two on day $k$. Person three
can have either of these birthdays, (probability $2/k$). So
$P(3) = (1/k)1 + (1-1/k)2/k$. Generally, either the first $n$ people share a
birthday, then the probability is 1. Otherwise, the $n+1$th person must share
a birthday with one of the first $n$ people, (whose birthdays are all distinct).
So $P(n+1) = P(n) + (1 - P(n))n/k$, or $P(n) = P(n - 1) + (1 - P(n - 1))(n - 1)/k$.

Now we can compute $P(n)$. Example implementation in python.

{% filter python_code %}
def birthday(n, k=365):
    if n == 1:
        return 0
    p = birthday(n - 1, k)
    return p + (1 - p) * ((n - 1) / float(k))
{% endfilter %}

{% filter python_repl %}
>>> birthday(1)
0
>>> birthday(2)
0.0027397260273972603
>>> birthday(3)
0.008204165884781385
{% endfilter %}

{% filter plot("Probability of a shared birthday.") %}
data = [birthday(n) for n in xrange(1, 80)]
plt.plot(data)
plt.xlabel("$n$")
plt.ylabel("$P(n)$")
{% endfilter %}
