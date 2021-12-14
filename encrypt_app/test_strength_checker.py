import unittest

from EncryptionServices.strength_checker import strength_checker
from EncryptionServices.password_gen import password_gen


class TestStrength(unittest.TestCase):

    def test_strength_checker(self):
        """
        Check if password generated is very strong
        :return:
        """
        passcode = password_gen()
        resp = strength_checker(passcode)
        self.assertEqual(resp['password'], passcode)
        self.assertEqual(resp["label"], "very strong")


if __name__ == '__main__':
    unittest.main()
