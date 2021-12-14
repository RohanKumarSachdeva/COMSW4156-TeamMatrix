import unittest
import json
import os

from app import get_app, clear_app


class TestApp(unittest.TestCase):

    def setUp(self):
        os.environ['DB_NAME'] = 'test_sqlite_db'
        self.app = get_app()
        self.user_email = 'testuser@xyz.com'

    def tearDown(self):
        clear_app(self.app.db)

    def test_hello(self):
        """
        Testing the root endpoint
        :return:
        """
        with self.app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.status_code, 200)

    def test_generate(self):
        """
        Testing the generate endpoint
        :return:
        """
        with self.app.test_client() as c:
            response = c.get('/generate')
            self.assertEqual(response.status_code, 200)

    def test_create_retrieve(self):
        """
        Testing the create and retrieve endpoint
        :return:
        """
        app_name = 'testapp'
        password = 'qwerty123'
        with self.app.test_client() as c:
            response = c.post(f'/create?application={app_name}'
                              f'&password={password}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            retrieved_password = data['data'][app_name]
            self.assertEqual(retrieved_password, password)

    def test_update(self):
        """
        Testing the update endpoint
        :return:
        """
        app_name = 'testapp'
        password = 'qwerty123'
        new_password = 'asdf4321'

        with self.app.test_client() as c:
            c.post(f'/create?application={app_name}&password={password}',
                   json={'user_email': self.user_email})

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            retrieved_password = data['data'][app_name]

            self.assertEqual(retrieved_password, password)
            self.assertNotEqual(retrieved_password, new_password)

            # Now updating the application password
            response = c.post(f'/update?application={app_name}&'
                              f'password={new_password}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            retrieved_password = data['data'][app_name]

            self.assertNotEqual(retrieved_password, password)
            self.assertEqual(retrieved_password, new_password)

    def test_delete(self):
        """
        Testing the delete endpoint
        :return:
        """
        app_name = 'testapp'
        password = 'qwerty123'

        with self.app.test_client() as c:
            c.post(f'/create?application={app_name}&password={password}',
                   json={'user_email': self.user_email})
            response = c.delete(f'/delete?application={app_name}',
                                json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            self.assertNotIn(app_name, data['data'])


if __name__ == '__main__':
    unittest.main()
