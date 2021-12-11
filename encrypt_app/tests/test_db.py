import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

import db

# Commit for testing
# Commiting to test github actions 1
class Test_Testdb(unittest.TestCase):

    def setUp(self):
        """
        Initializes the database
        """
        db.init_db()

    def tearDown(self):
        """
        Clears the database
        """
        db.clear()

    def test_add_record(self):
        """
        Test whether a given record was added to DB
        """
        record = ('user1', 'app1', 'pass1', 'key1')
        db.add_record(record)
        record_returned = db.get_record(record[0], record[1])[0]
        self.assertEqual((record[2], record[3]),
                         (record_returned[1], record_returned[2]))

    def test_update_record(self):
        """
        Test whether password was updated correctly in DB
        """
        record = ('user1', 'app1', 'pass1', 'key1')
        db.add_record(record)
        new_record = (record[0], record[1], 'pass2', 'key2')
        db.update_record(new_record)
        record_returned = db.get_record(record[0], record[1])[0]
        self.assertEqual((new_record[2], new_record[3]),
                         (record_returned[1], record_returned[2]))

    def test_delete_record(self):
        """
        Test whether the given record is deleted from DB
        """
        record = ('user1', 'app1', 'pass1', 'key1')
        db.add_record(record)
        db.delete_record(record[0], record[1])
        record_returned = db.get_record(record[0], record[1])
        self.assertEqual(0, len(record_returned))


if __name__ == '__main__':
    unittest.main()
