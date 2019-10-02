import json
import os
from os import path
import unittest
import importlib
import ast
import astor

INDEX_TO_FIRST_NAME = 1
INDEX_TO_LAST_NAME = 0
INDEX_TO_MAIL = 2
INDEX_TO_FIRST_ANSWER = 8
INDEX_TO_LAST_ANSWER = 11

MAIN_STRING = """\
if __name__ == "__main__":
    pass
"""

CURRENT_FILE_ABS_PATH = path.dirname(path.abspath(__file__))
RELATIVE_PATH_TO_DATA_FOLDER = "./data/"
RELATIVE_PATH_TO_STUDENT_ANSWERS = "./student_answers/"
DATA_FILE_NAME = "TC-3-I-PIT-Validation 3-réponses.json"
ABS_PATH_TO_DATA_FOLDER = path.join(CURRENT_FILE_ABS_PATH, RELATIVE_PATH_TO_DATA_FOLDER)
ABS_PATH_TO_DATA_FILE = path.join(ABS_PATH_TO_DATA_FOLDER, DATA_FILE_NAME)
ABS_PATH_TO_STUDENT_ANSWERS = path.join(CURRENT_FILE_ABS_PATH, RELATIVE_PATH_TO_STUDENT_ANSWERS)


def code_has_main(code):
    ast_tree = ast.parse(source=code, filename="<string>", mode="exec")

    for python_code_body_element in ast_tree.body:
        if isinstance(python_code_body_element, ast.If):
            try:
                if (python_code_body_element.test.comparators[0].s == "__main__"
                        and python_code_body_element.test.left.id == "__name__"):
                    return True
            except AttributeError:
                pass
    return False


def fix_code_to_add_main(code):
    ast_tree = ast.parse(source=code, filename="<string>", mode="exec")

    main_element = ast.parse(source=MAIN_STRING, filename="<string>", mode="exec").body[0]
    main_element.body.pop(0)

    body = []

    for body_element in ast_tree.body:
        if (not isinstance(body_element, ast.FunctionDef)
                and not isinstance(body_element, ast.ClassDef)
                and not isinstance(body_element, ast.Import)
                and not isinstance(body_element, ast.ImportFrom)):
            main_element.body.append(body_element)
        else:
            body.append(body_element)

    body.append(main_element)

    ast_tree.body = body

    return astor.to_source(ast_tree, indent_with=' ' * 4, add_line_information=False)


if __name__ == "__main__":
    if not os.path.exists(ABS_PATH_TO_DATA_FOLDER):
        os.makedirs(ABS_PATH_TO_DATA_FOLDER)
        raise FileNotFoundError("You did not have a data folder at the project root: it has been created for you, \
        you now only have to copy paste the test results data file.")

    if not os.path.exists(ABS_PATH_TO_STUDENT_ANSWERS):
        os.makedirs(ABS_PATH_TO_STUDENT_ANSWERS)

    with open(ABS_PATH_TO_DATA_FILE) as json_file:
        data = json.load(json_file)
        for student_participation in data[0]:
            counter = 1
            for i in range(INDEX_TO_FIRST_ANSWER, INDEX_TO_LAST_ANSWER + 1):
                # Write student answer in python file
                student_answer_python_code = student_participation[i]

                abs_path_to_python_answer_file = path.join(
                    CURRENT_FILE_ABS_PATH, RELATIVE_PATH_TO_STUDENT_ANSWERS + "question_" + str(counter) + ".py")

                with open(abs_path_to_python_answer_file, "w") as student_answer_python_file:
                    # Fix strange space character in original data
                    student_answer_python_code = student_answer_python_code.replace(u"\u00a0", " ")

                    # Fix absence of """ if __name__ == "__main__": """ expression before executed code and report it
                    try:
                        if not code_has_main(student_answer_python_code):
                            print(
                                "Student {first_name} {last_name} forgot 'main' in question {question_number}".format(
                                    first_name=student_participation[INDEX_TO_FIRST_NAME],
                                    last_name=student_participation[INDEX_TO_LAST_NAME],
                                    question_number=counter
                                ))
                            print("Fixing their code to allow for proper testing...")
                            student_answer_python_code = fix_code_to_add_main(student_answer_python_code)
                            print("...Code fixed !")
                    except SyntaxError as e:
                        # If the code was not properly formatted and the AST could not be built...
                        print(
                            "Student {first_name} {last_name} wrote uninterpretable code for question {question_number}".format(
                                first_name=student_participation[INDEX_TO_FIRST_NAME],
                                last_name=student_participation[INDEX_TO_LAST_NAME],
                                question_number=counter
                            ))
                        print("Printing said code... :")
                        print(student_answer_python_code)

                    # Write student code into python file
                    student_answer_python_file.write(student_answer_python_code)

                # Get and run test module corresponding to question
                test_module_name = "verification_tests.question_" + str(counter) + "_test"

                test_module = importlib.import_module(test_module_name)

                test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
                unittest.TextTestRunner(verbosity=2).run(test_suite)

                # Increment counter for next question loop
                counter += 1

