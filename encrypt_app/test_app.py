import unittest
from app import get_app
import db

app = get_app()
class Test_App(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello(self):
        with app.test_client() as c:
            response = c.get('/')
            print(response.data)
            self.assertEqual(response.status_code, 200)

    def test_create(self):
        with app.test_client() as c:
            response = c.post('/create?application=Twitter&password=Qwerty123')
            print(response.data)
            self.assertEqual(response.status_code, 200)

    def test_retrieve(self):
        with app.test_client() as c:
            response = c.get('/retrieve?application=Twitter')
            print(response.data)
            self.assertEqual(response.status_code, 200)

    def test_update(self):
        with app.test_client() as c:
            response = c.post('/update?application=Twitter&password=123Qwerty')
            print(response.data)
            self.assertEqual(response.status_code, 200)

    def test_delete(self):
        with app.test_client() as c:
            response = c.delete('/delete?application=Twitter')
            print(response.data)
            self.assertEqual(response.status_code, 200)

    def test_generate(self):
        with app.test_client() as c:
            response = c.get('/generate')
            print(response.data)
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
