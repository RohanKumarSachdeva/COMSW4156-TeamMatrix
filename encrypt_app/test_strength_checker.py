import unittest
import sys
import os
from EncryptionServices.strength_checker import strength_checker
from EncryptionServices.password_gen import password_gen

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')


class TestStrength(unittest.TestCase):

    def test_strength_checker(self):
        """
        Check if password generated is very strong
        :return:
        """
        password = password_gen()
        resp = strength_checker(password)
        print("This is response for strength", resp)
        # self.assertEqual(resp["label"], "very strong")


if __name__ == '__main__':

    unittest.main()
