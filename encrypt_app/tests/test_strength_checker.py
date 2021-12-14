import unittest
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from EncryptionServices.password_gen import password_gen
from EncryptionServices.strength_checker import strength_checker

class TestStrength(unittest.TestCase):
    def test_strength_checker(self):
        """
        Check if password generated is very strong
        :return:
        """
        password = password_gen()
        resp = strength_checker(password)
        self.assertEqual(resp["label"], "very strong")

if __name__ == '__main__':
    unittest.main()
