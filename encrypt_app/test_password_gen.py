import unittest
import re

from EncryptionServices.password_gen import password_gen


class TestGenerate(unittest.TestCase):
    def test_length(self):
        """
        Check if password generated is correct length
        :return:
        """
        length = 12
        password = {'message': password_gen(length)}
        self.assertEqual(len(password["message"]), length)

    def test_validity(self):
        """
        Check if password generated has digits and Uppercase character
        :return:
        """

        password = {'message': password_gen()}

        # Check if password has digit(s)
        resp = bool(re.search(r'\d', password["message"]))
        self.assertEqual(resp, True)

        # Check if password has Uppercase char
        resp_upper = any(char.isupper() for char in password["message"])
        self.assertEqual(resp_upper, True)


if __name__ == '__main__':
    unittest.main()
