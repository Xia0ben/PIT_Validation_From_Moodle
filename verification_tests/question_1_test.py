import unittest
import unittest.mock
import io
import math
import re

from student_answers import question_1


class Question1Test(unittest.TestCase):
    STUDENT_CODE_FILE_PATH = "../student_answers/question_1.py"

    def find_student_factorial(self):
        for name in dir(question_1):
            if name.startswith("fact"):
                return getattr(question_1, name)
        raise NameError("Factorial not found")

    def test_factorielle(self):
        try:
            factorielle = self.find_student_factorial()
            for i in range(100):
                self.assertEqual(math.factorial(i), factorielle(i))
        except NameError as e:
            print("ERROR : STUDENT DID NOT DEFINE FACTORIELLE FUNCTION !")

    def test_main(self):
        outmock = io.StringIO()
        with unittest.mock.patch("builtins.input", side_effect=(str(i) for i in range(10,100))):
            with unittest.mock.patch("sys.stdout", new=outmock):
                for i in range(10,100):
                    question_1.main()
        outmock.seek(0)
        pat = re.compile(r"""\d+(\.\d+)?""")
        for line in outmock:
            res = pat.search(line)
            self.assertAlmostEqual(float(res.group(0)), math.e, 5)


if __name__ == '__main__':
    unittest.main()
