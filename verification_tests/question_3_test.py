import unittest
import unittest.mock
import io
import re
import random

from fixed_student_answers import question_3


class Question3Test(unittest.TestCase):
    def test_func_name(self):
        self.assertIn("minMaxMoy", dir(question_3))

    def test_minMaxMoy(self):
        for rand_list in ([random.randint(0,100) for _ in range(random.randint(5,40))] for _ in range(50)):
            self.assertEqual(question_3.minMaxMoy(rand_list),
                    (min(rand_list), max(rand_list), sum(rand_list) / len(rand_list)))

    def test_main(self):
        outmock = io.StringIO()
        with unittest.mock.patch("sys.stdout", outmock):
            question_3.main()
        outmock.seek(0)
        pat = re.compile(r"10.*20.*15")
        for line in outmock:
            res = pat.search(line)
            self.assertIsNotNone(res)


if __name__ == '__main__':
    unittest.main()
