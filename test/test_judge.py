import unittest

from src.judge import judge
from src import sandbox_db


class JudgeTestCase(unittest.TestCase):
    # 1行だけの場合
    def test_one_record(self):
        expected = [(1, 'Taro')]
        answered = [(1, 'Taro')]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertTrue(correct)
        self.assertIsNone(wrong_line)

    def test_one_record_incorrect_value_1(self):
        expected = [(1, 'Taro')]
        answered = [(1, 'Jiro')]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertFalse(correct)
        self.assertEqual(1, wrong_line)

    def test_one_record_incorrect_value_2(self):
        expected = [(1, 'Taro')]
        answered = [(2, 'Taro')]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertFalse(correct)
        self.assertEqual(1, wrong_line)

    # 2行以上の場合
    def test_two_records(self):
        expected = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        answered = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertTrue(correct)
        self.assertIsNone(wrong_line)

    def test_two_records_unordered_non_strict(self):
        """
        順序を求めない問題の場合，順序が違っていても正解
        """
        expected = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        answered = [
            (2, 'Jiro'),
            (1, 'Taro'),
        ]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertTrue(correct)
        self.assertIsNone(wrong_line)

    def test_two_records_unordered_strict(self):
        """
        順序を求める問題の場合，順序が違っていたら不正解
        """
        expected = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        answered = [
            (2, 'Jiro'),
            (1, 'Taro'),
        ]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=True)
        self.assertFalse(correct)
        self.assertEqual(1, wrong_line)

    def test_duplicated_records(self):
        """
        ある行が不必要に重複して存在する場合，もちろん不正解
        """
        expected = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        answered = [
            (1, 'Taro'),
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertFalse(correct)
        self.assertEqual(2, wrong_line)

    def test_two_records_duplicated_unordered_non_strict(self):
        expected = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        answered = [
            (2, 'Jiro'),
            (1, 'Taro'),
            (1, 'Taro'),
        ]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertFalse(correct)
        self.assertEqual(3, wrong_line)

    def test_two_records_insufficient(self):
        expected = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        answered = [
            (1, 'Taro'),
        ]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertFalse(correct)
        self.assertEqual(2, wrong_line)

    def test_two_records_extra(self):
        expected = [
            (1, 'Taro'),
        ]
        answered = [
            (1, 'Taro'),
            (2, 'Jiro'),
        ]
        correct, wrong_line = judge(expected=expected, answered=answered, order_strict=False)
        self.assertFalse(correct)
        self.assertEqual(2, wrong_line)

    def test_real_1(self):
        ddl = [
            "create table Students (",
            "    id int primary key,",
            "    name varchar(16) unique",
            ");",
            "create table LivesIn (",
            "    id int primary key,",
            "    place varchar(16),",
            "    foreign key(id) references Students(id)",
            ");"
        ]

        tables = [
            {
                "name": "Students",
                "columns": ["id", "name"],
                "records": [
                    [1, "David"],
                    [2, "Charlie"],
                    [3, "Bob"],
                    [4, "Alice"]
                ]
            },
            {
                "name": "LivesIn",
                "columns": ["id", "place"],
                "records": [
                    [1, "Detroit"],
                    [2, "Birmingham"],
                    [3, "Canberra"],
                    [4, "Birmingham"]
                ]
            }
        ]

        query = """
select Students.name, LivesIn.place
from Students
join LivesIn on Students.id = LivesIn.id
where LivesIn.place = 'Birmingham'
order by Students.name asc;
"""

        expected = [
            ("Alice", "Birmingham"),
            ("Charlie", "Birmingham")
        ]

        result: sandbox_db.Result = sandbox_db.execute(ddl=ddl, tables=tables, query=query)
        self.assertFalse(result.has_error)

        correct, wrong_line = judge(expected=expected, answered=result.records, order_strict=True)
        self.assertTrue(correct)


if __name__ == '__main__':
    unittest.main()
