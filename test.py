"""
>>> cool(3)
[0, 1, 4]
"""

def cool(n):
    return [x * x for x in range(n)]

import doctest
doctest.testmod()
