---
title: First Post!
date: 2015-02-01
categories: [python]
---

Here is an example of some python code.

```python
def fact(n):
    if n == 0:
        return 1
    return n * fact(n - 1)
```

And here is how to use it!

```python
>>> fact(0)
1
>>> fact(5)
120
```

Here's a bash example.

```python
{{ "posts/first.py"|include_file }}
```

```{.terminal}
$ cat first.py
print 'hello world!'
$ python first.py
hello world!
```

{% filter dot("Embedded dot diagram!") %}
digraph {
    a -> b -> c;
    a -> c;
}
{% endfilter %}

That's it!
