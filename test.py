

import unittest
import tornado.testing
import logging
import os

def all():
    t = unittest.TestLoader()
    return t.discover( os.getcwd() + '/tests/', '*test.py')

if __name__ == '__main__':
	logging.getLogger().setLevel(logging.DEBUG)
	tornado.testing.main()



