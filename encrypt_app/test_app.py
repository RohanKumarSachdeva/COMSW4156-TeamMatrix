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

            spchar = True
            length = 's'
            response = c.get(f'/generate?spchar={spchar}'
                             f'&len={length}')
            self.assertEqual(response.status_code, 400)

            spchar = True
            length = 1
            response = c.get(f'/generate?spchar={spchar}'
                             f'&len={length}')
            self.assertEqual(response.status_code, 400)

            spchar = True
            length = 123
            response = c.get(f'/generate?spchar={spchar}'
                             f'&len={length}')
            self.assertEqual(response.status_code, 400)

            spchar = ''
            response = c.get(f'/generate?spchar={spchar}')
            self.assertEqual(response.status_code, 400)

    def test_create_retrieve(self):
        """
        Testing the create and retrieve endpoint
        :return:
        """
        app_name = 'testapp'
        passcode = 'qwerty123'
        with self.app.test_client() as c:
            response = c.post(f'/create?application={app_name}'
                              f'&password={passcode}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            retrieved_password = data['data'][app_name]
            self.assertEqual(retrieved_password, passcode)

            response = c.post(f'/create?application='
                              f'&password={passcode}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            response = c.post(f'/create?application=all'
                              f'&password={passcode}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            response = c.post(f'/create?application={app_name}'
                              f'&password=1',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            response = c.post(f'/create?application={app_name}'
                              f'&password=1234567890124567',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            passcode2 = 'pass"pass'
            response = c.post(f'/create?application={app_name}'
                              f'&password={passcode2}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            response = c.post(f'/create?application={app_name}'
                              f'&password={passcode}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            app_name = ''
            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})

    def test_update(self):
        """
        Testing the update endpoint
        :return:
        """
        app_name = 'testapp'
        passcode = 'qwerty123'
        new_passcode = 'asdf4321'

        with self.app.test_client() as c:
            c.post(f'/create?application={app_name}&password={passcode}',
                   json={'user_email': self.user_email})

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            retrieved_password = data['data'][app_name]

            self.assertEqual(retrieved_password, passcode)
            self.assertNotEqual(retrieved_password, new_passcode)

            # Now updating the application password
            response = c.post(f'/update?application={app_name}&'
                              f'password={new_passcode}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            retrieved_password = data['data'][app_name]

            self.assertNotEqual(retrieved_password, passcode)
            self.assertEqual(retrieved_password, new_passcode)

            response = c.post(f'/update?application=&'
                              f'password={new_passcode}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            response = c.post(f'/update?application={app_name}&'
                              f'password=1',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            response = c.post(f'/update?application={app_name}&'
                              f'password=1234567890124567',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            passcode2 = 'pass"pass'
            response = c.post(f'/update?application={app_name}&'
                              f'password={passcode2}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            app_name2 = 'test123'
            response = c.post(f'/update?application={app_name2}&'
                              f'password={passcode2}',
                              json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

    def test_delete(self):
        """
        Testing the delete endpoint
        :return:
        """
        app_name = 'testapp'
        passcode = 'qwerty123'

        with self.app.test_client() as c:
            c.post(f'/create?application={app_name}&password={passcode}',
                   json={'user_email': self.user_email})
            response = c.delete(f'/delete?application={app_name}',
                                json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            data = json.loads(response.data.decode())
            self.assertNotIn(app_name, data['data'])

            app_name2 = ''
            response = c.delete(f'/delete?application={app_name2}',
                                json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)

            c.post(f'/create?application={app_name}&password={passcode}',
                   json={'user_email': self.user_email})
            response = c.delete(f'/delete?application={app_name}',
                                json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            response = c.get(f'/retrieve?application={app_name}',
                             json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

    def test_strength(self):
        """
        Testing the strength checker endpoint
        :return:
        """
        passcode = 'qwerty123'
        with self.app.test_client() as c:
            response = c.get(f'/strength?password={passcode}',
                             json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 200)

            passcode = ''
            response = c.get(f'/strength?password={passcode}',
                             json={'user_email': self.user_email})
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
