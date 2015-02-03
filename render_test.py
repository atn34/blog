#!/usr/bin/env python
import unittest
import doctest

import render

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(render))
    return tests

unittest.main()
