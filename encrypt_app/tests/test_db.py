import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

import db

# Commit for testing
# Commiting to test github actions 7
class Test_Testdb(unittest.TestCase):

    def setUp(self):
        """
        Initializes the database
        """
        self.db = 'test_sqlite_db'
        db.init_db(self.db)

    def tearDown(self):
        """
        Clears the database
        """
        db.clear(self.db)

    def test_add_record(self):
        """
        Test whether a given record was added to DB
        """
        record = ('user1', 'app1', 'pass1', 'key1')
        db.add_record(self.db, record)
        record_returned = db.get_record(self.db, record[0], record[1])[0]
        self.assertEqual((record[2], record[3]),
                         (record_returned[1], record_returned[2]))

    def test_update_record(self):
        """
        Test whether password was updated correctly in DB
        """
        record = ('user1', 'app1', 'pass1', 'key1')
        db.add_record(self.db, record)
        new_record = (record[0], record[1], 'pass2', 'key2')
        db.update_record(self.db, new_record)
        record_returned = db.get_record(self.db, record[0], record[1])[0]
        self.assertEqual((new_record[2], new_record[3]),
                         (record_returned[1], record_returned[2]))

    def test_delete_record(self):
        """
        Test whether the given record is deleted from DB
        """
        record = ('user1', 'app1', 'pass1', 'key1')
        db.add_record(self.db, record)
        db.delete_record(self.db, record[0], record[1])
        record_returned = db.get_record(self.db, record[0], record[1])
        self.assertEqual(0, len(record_returned))


if __name__ == '__main__':
    unittest.main()
