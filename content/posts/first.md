---
title: First Post!
date: 2015-02-01
categories: [python]
---

Here is an example of some python code.

{% filter python_code %}
def fact(n):
    if n == 0:
        return 1
    return n * fact(n - 1)
{% endfilter %}

And here is how to use it!

{% filter python_repl %}
>>> fact(0)
1
>>> fact(5)
120
{% endfilter %}

Here's a bash example.

```python
{{ "posts/first.py"|include_file }}
```

{% filter bash_prompt %}
$ cat first.py
print 'hello world!'
$ python first.py
hello world!
{% endfilter %}

{% filter dot("Embedded dot diagram!") %}
graph {
    a0 -- b0
    a0 -- b1
    a0 -- b2
    a0 -- b3
    a1 -- b0
    a1 -- b1
    a1 -- b2
    a1 -- b3
    a2 -- b0
    a2 -- b1
    a2 -- b2
    a2 -- b3
    a3 -- b0
    a3 -- b1
    a3 -- b2
    a3 -- b3
}
{% endfilter %}

{% filter plot("Embedded plot!") %}
import random
data = [random.random() for x in xrange(100)]
plt.plot(data)
{% endfilter %}

That's it!
