import unittest
import unittest.mock
import io
import re

from fixed_student_answers import question_2


class Question2Test(unittest.TestCase):
    def find_student_valid(self):
        for name in dir(question_2):
            if "valid" in name:
                return getattr(question_2, name)
        raise NameError("valide not found")

    def test_func_names(self):
        self.assertIn("valide", dir(question_2))
        self.assertIn("saisie", dir(question_2))
        self.assertIn("proportion", dir(question_2))

    def test_valide(self):
        valide = self.find_student_valid()
        self.assertTrue(valide("acgtgatcgattggatccgattaa"))
        self.assertFalse(valide("acgtgxatcgyatuitggatkccgattaa"))
        self.assertFalse(valide(""))

    def test_saisie(self):
        inputs = ("xhxhgghhxa", "acgtagatcgat", "atgactgatcgctatggc", "agtcgattaggccta", "actgtatgcgc")
        with unittest.mock.patch("builtins.input", side_effect=inputs):
            for i in inputs[1:]:
                self.assertEqual(question_2.saisie(), i)

    def test_proportion(self):
        self.assertIn(question_2.proportion("agagagag", "ag"), (0.5, 50))
        self.assertIn(question_2.proportion("agabtcga", "ag"), (0.125, 12.5))
        self.assertEqual(question_2.proportion("agabtcga", "ac"), 0)
        self.assertIn(question_2.proportion("agggaabtatggctaaatga", "atgg"), (0.05, 5))


    def test_main(self):
        outmock = io.StringIO()
        with unittest.mock.patch("builtins.input", side_effect=("tgtgaactgagtaagt", "agt")):
            with unittest.mock.patch("sys.stdout", new=outmock):
                question_2.main()
        outmock.seek(0)
        pat = re.compile(r"""\d+(\.\d+)?\s*%""")
        for line in outmock:
            res = pat.search(line)
            self.assertIsNotNone(res)
            self.assertAlmostEqual(float(res.group(0)[:-1]), 12.5)


if __name__ == '__main__':
    unittest.main()
