---
title: The Birthday Problem
date: 2015-02-07
categories: [probability]
---

# The Birthday Problem #

Suppose there are $n$ people in a room, in a world with $k$ days in a year.
What's the probability that two people share a birthday? Assume that birthdays
are uniformly distributed throughout the year.

For $n \leq 1$, $P(0) = P(1) = 0$, as there aren't even two people.
For $n > 1$, let's consider two events.

- Event 1: There is a birthday shared among the first $n - 1$ people. (Probability is $P(n)$).
- Event 2: There is not a birthday shared among the first $n - 1$ people. (Probability is $1 - P(n)$).

Since these events are mutually exclusive, we can add the probability of a shared birthday
in each event to get $P(n)$. In event 1, the probability of a shared birthday is $1$. In
event 2, each of the first $n - 1$ people has a distinct birthday. So the probability of a
shared birthday is the probability that the $n$th person shares a birthday with one of the
first $n - 1$ people: $(n - 1)/k$.

Therefore $P(n) = P(n - 1) + (1 - P(n - 1))(n - 1)/k$.

Now we can compute $P(n)$. Example implementation in python.

{% filter python_code %}
def birthday(n, k=365):
    """
    The probability that n people share a birthday if there are k days in the year.
    """
    if n == 0:
        return 0
    p = birthday(n - 1, k)
    return p + (1 - p) * ((n - 1) / float(k))
{% endfilter %}

Some examples.

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
