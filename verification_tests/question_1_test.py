import unittest
import unittest.mock
import io
import fixed_student_answers.question_1 as question_1


class Question1Test(unittest.TestCase):
    STUDENT_CODE_FILE_PATH = "../student_answers/question_1.py"

    def find_student_factorial(self):
        for name in dir(question_1):
            if name.startswith("fact"):
                return getattr(question_1, name)
        raise NameError("Factorial not found")

    def test_factorielle(self):
        from math import factorial

        try:
            factorielle = self.find_student_factorial()
            for i in range(100):
                self.assertEqual(factorial(i), factorielle(i))
        except NameError as e:
            print("ERROR : STUDENT DID NOT DEFINE FACTORIELLE FUNCTION !")

    def test_main(self):
        outmock = io.StringIO
        with unittest.mock.patch("builtins.input", side_effect=(str(i) for i in range(100))):
            with unittest.mock.patch("sys.stdout", new=outmock):
                for i in range(100):
                    question_1.main()
            outmock.seek(0)
            print(outmock.read())



    # def test_main(self):
    #     current_file_abs_path = path.dirname(path.abspath(__file__))
    #     abs_path_to_data_file = path.join(current_file_abs_path, self.STUDENT_CODE_FILE_PATH)
    #
    #     p = Popen(['/usr/bin/python', abs_path_to_data_file], stdin=PIPE, stdout=PIPE)
    #     # p = subprocess.run(['/usr/bin/python', abs_path_to_data_file])
    #     p.stdin.write("20\n".encode(encoding='UTF-8'))
    #     output = p.stdout.read()
    #
    #     self.assertEqual(output, 0)


if __name__ == '__main__':
    unittest.main()
