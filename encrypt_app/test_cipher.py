import unittest

from EncryptionServices.cipher import Cipher


class TestCipher(unittest.TestCase):
    def setUp(self):
        self.crypt = Cipher()

    def test_valid_encryption(self):
        """
        Test for encryption and decryption with valid key
        :return:
        """
        plaintext_passcode = "Qwerty123"
        e_password, key = self.crypt.encipher(plaintext_passcode)
        self.assertEqual(self.crypt.decipher(e_password), plaintext_passcode)

    def test_invalid_decryption(self):
        """
        Test for encryption and decryption with invalid key
        :return:
        """
        plaintext_passcode = "Qwerty123"
        e_password, key = self.crypt.encipher(plaintext_passcode)
        # Creating new key for decryption
        crypt2 = Cipher()
        with self.assertRaises(Exception):
            crypt2.decipher(e_password)


if __name__ == '__main__':
    unittest.main()
