#!/usr/bin/env python
import unittest
import doctest
import jinja

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(jinja))
    return tests

unittest.main()
