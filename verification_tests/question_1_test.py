import unittest
import student_answers.question_1 as question_1


class Question1Test(unittest.TestCase):
    STUDENT_CODE_FILE_PATH = "../student_answers/question_1.py"

    def test_factorielle(self):
        from math import factorial

        for i in range(100):
            try:
                self.assertEqual(factorial(i), question_1.factorielle(i))
            except NameError as e:
                print("ERROR : STUDENT DID NOT DEFINE FACTORIELLE FUNCTION !")


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