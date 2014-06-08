import unittest

tests = unittest.TestLoader().discover('.', '*_test.py')
unittest.TextTestRunner().run(tests)
