import glob
import re
import unittest

from fastapi.testclient import TestClient

from src.app import app

"""
Start database before you run tests.
After run tests, stop database.

"""


class AppTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_read_main(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # API methods
    def test_get_problem(self):
        response = self.client.get(
            "/api/v1/problem",
            params={'problem_name': 'entry-1'}
        )
        with open('problems/entry-1.json', 'r') as f:
            problem = f.read()
        self.assertEqual(
            response.text.replace('\n', '').replace(' ', ''),
            problem.replace('\n', '').replace(' ', '')
        )

    def test_get_problem_list(self):
        response = self.client.get('/api/v1/problem_list')
        problems = list(map(lambda x: x.rstrip('.json').split('/')[-1], glob.glob('problems/*.json')))
        self.assertListEqual(
            sorted(eval(response.text)['problems']),
            sorted(problems)
        )

    def test_get_info(self):
        response = self.client.get('/api/v1/info')
        self.assertTrue(re.match(
            'PostgreSQL \d\d\.\d',
            eval(response.text)['version'])
        )

    def test_test_answer(self):
        response = self.client.post(
            '/api/v1/test',
            data={
                'problem_name': 'entry-1',
                'answer': 'SELECT name FROM Students;'
            }
        )
        result = eval(response.text.replace('null', 'None'))
        self.assertEqual(result['result'], 'AC')
        self.assertEqual(result['wrong_line'], None)
        self.assertEqual(result['answer_columns'], ['name'])
        self.assertEqual(result['answer_records'], [["Alice"], ["Bob"], ["Charlie"], ["David"]])

        response = self.client.post(
            '/api/v1/test',
            data={
                'problem_name': 'entry-1',
                'answer': 'SELECT id FROM Students;'
            }
        )
        result = eval(response.text.replace('null', 'None'))
        self.assertEqual(result['result'], 'WA')
        self.assertEqual(result['wrong_line'], 1)
        self.assertEqual(result['answer_columns'], ['id'])
        self.assertEqual(result['answer_records'], [[1], [2], [3], [4]])

        response = self.client.post(
            '/api/v1/test',
            data={
                'problem_name': 'entry-1',
                'answer': 'SELECT name FROM People;'
            }
        )
        result = eval(response.text.replace('null', 'None'))
        self.assertEqual(result['result'], 'PE')


if __name__ == '__main__':
    unittest.main()
