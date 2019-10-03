import json
import os
from os import path
import shutil
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

MAIN_FUNCTION ="""\
def main():
    pass
"""

CURRENT_FILE_ABS_PATH = path.dirname(path.abspath(__file__))
RELATIVE_PATH_TO_DATA_FOLDER = "./data/"
RELATIVE_PATH_TO_ORIGINAL_STUDENT_ANSWERS = "./original_student_answers/"
RELATIVE_PATH_TO_FIXED_STUDENT_ANSWERS = "./fixed_student_answers/"
DATA_FILE_NAME = "TC-3-I-PIT-Validation 3-réponses.json"
ABS_PATH_TO_DATA_FOLDER = path.join(CURRENT_FILE_ABS_PATH, RELATIVE_PATH_TO_DATA_FOLDER)
ABS_PATH_TO_DATA_FILE = path.join(ABS_PATH_TO_DATA_FOLDER, DATA_FILE_NAME)
ABS_PATH_TO_ORIGINAL_STUDENT_ANSWERS = path.join(CURRENT_FILE_ABS_PATH, RELATIVE_PATH_TO_ORIGINAL_STUDENT_ANSWERS)
ABS_PATH_TO_FIXED_STUDENT_ANSWERS = path.join(CURRENT_FILE_ABS_PATH, RELATIVE_PATH_TO_FIXED_STUDENT_ANSWERS)


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


def fix_code_to_ensure_all_calls_in_main(code):
    ast_tree = ast.parse(source=code, filename="<string>", mode="exec")

    main_element = None

    main_element_body_additions = []

    body = []

    for body_element in ast_tree.body:
        if (not isinstance(body_element, ast.FunctionDef)
                and not isinstance(body_element, ast.ClassDef)
                and not isinstance(body_element, ast.Import)
                and not isinstance(body_element, ast.ImportFrom)
                and not isinstance(body_element, ast.If)):
            main_element_body_additions.append(body_element)
        else:
            if isinstance(body_element, ast.If):
                try:
                    if (body_element.test.comparators[0].s == "__main__"
                            and body_element.test.left.id == "__name__"):
                        main_element = body_element
                        body.append(body_element)
                except AttributeError:
                    main_element_body_additions.append(body_element)
            else:
                body.append(body_element)

    for element in main_element_body_additions:
        main_element.body.insert(0, element)

    ast_tree.body = body

    return astor.to_source(ast_tree, indent_with=' ' * 4, add_line_information=False)

def fix_code_to_remove_functions_from_main(code):
    ast_tree = ast.parse(source=code, filename="<string>", mode="exec")

    # Find main if statement
    for python_code_body_element in ast_tree.body:
        if isinstance(python_code_body_element, ast.If):
            try:
                if (python_code_body_element.test.comparators[0].s == "__main__"
                        and python_code_body_element.test.left.id == "__name__"):
                    main_if_element = python_code_body_element
                    main_non_function_elements = []
                    for element in main_if_element.body:
                        if isinstance(element, ast.FunctionDef):
                            ast_tree.body.append(element)
                        else:
                            main_non_function_elements.append(element)
                    main_if_element.body = main_non_function_elements
            except AttributeError:
                pass

    return astor.to_source(ast_tree, indent_with=' ' * 4, add_line_information=False)


def transform_main_to_function(code):
    ast_tree = ast.parse(source=code, filename="<string>", mode="exec")

    main_function_element = ast.parse(source=MAIN_FUNCTION, filename="<string>", mode="exec").body[0]
    main_function_element.body.pop(0)

    for python_code_body_element in ast_tree.body:
        if isinstance(python_code_body_element, ast.If):
            try:
                if (python_code_body_element.test.comparators[0].s == "__main__"
                        and python_code_body_element.test.left.id == "__name__"):
                    main_if_element = python_code_body_element
                    main_function_element.body = main_if_element.body
                    ast_tree.body.remove(main_if_element)
                    ast_tree.body.append(main_function_element)
                    break
            except AttributeError:
                pass

    return astor.to_source(ast_tree, indent_with=' ' * 4, add_line_information=False)


def validate_answers_for_students_emails(students_emails, interactive=False):
    if not os.path.exists(ABS_PATH_TO_DATA_FOLDER):
        os.makedirs(ABS_PATH_TO_DATA_FOLDER)
        raise FileNotFoundError("You did not have a data folder at the project root: it has been created for you, \
        you now only have to copy paste the test results data file.")

    if not os.path.exists(ABS_PATH_TO_ORIGINAL_STUDENT_ANSWERS):
        os.makedirs(ABS_PATH_TO_ORIGINAL_STUDENT_ANSWERS)

    if not os.path.exists(ABS_PATH_TO_FIXED_STUDENT_ANSWERS):
        os.makedirs(ABS_PATH_TO_FIXED_STUDENT_ANSWERS)

    with open(ABS_PATH_TO_DATA_FILE) as json_file:
        data = json.load(json_file)
        for student_participation in data[0]:
            # Only validate for given list of students, or validate for all if list is empty
            if students_emails and student_participation[INDEX_TO_MAIL] not in students_emails:
                continue

            # CLEANUP Empty student answers folders
            for entry in os.scandir(ABS_PATH_TO_ORIGINAL_STUDENT_ANSWERS):
                if entry.is_file():
                    os.remove(entry.path)
                elif entry.is_dir():
                    shutil.rmtree(entry.path)

            for entry in os.scandir(ABS_PATH_TO_FIXED_STUDENT_ANSWERS):
                if entry.is_file():
                    os.remove(entry.path)
                elif entry.is_dir():
                    shutil.rmtree(entry.path)

            if path.isfile("premierspremiers.txt"):
                os.remove("premierspremiers.txt")

            print("\n---------------------------------------------------------------------------"
                  + "\nPrinting validation results for student {first_name} {last_name}\n".format(
                    first_name=student_participation[INDEX_TO_FIRST_NAME],
                    last_name=student_participation[INDEX_TO_LAST_NAME],
                    )
                  + "---------------------------------------------------------------------------\n")

            counter = 1
            for i in range(INDEX_TO_FIRST_ANSWER, INDEX_TO_LAST_ANSWER + 1):

                if interactive:
                    input()

                # Write student answer in python file
                student_answer_python_code = student_participation[i]

                # Fix strange space character in original data
                student_answer_python_code = student_answer_python_code.replace(u"\u00a0", " ")

                abs_path_to_python_original_answer_file = path.join(
                    CURRENT_FILE_ABS_PATH, RELATIVE_PATH_TO_ORIGINAL_STUDENT_ANSWERS + "question_" + str(counter) + ".py")
                with open(abs_path_to_python_original_answer_file, "w") as student_answer_python_file:
                    student_answer_python_file.write(student_answer_python_code)

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

                    # For rednecks that put their functions in the main if statement...
                    student_answer_python_code = fix_code_to_remove_functions_from_main(student_answer_python_code)

                    # For rednecks that put statements other than functions, imports and classes outside of main...
                    student_answer_python_code = fix_code_to_ensure_all_calls_in_main(student_answer_python_code)

                    # Change main "if" statement to a main() function for easier testing
                    student_answer_python_code = transform_main_to_function(student_answer_python_code)

                    # Write student code into python file
                    abs_path_to_python_fixed_answer_file = path.join(
                        CURRENT_FILE_ABS_PATH,
                        RELATIVE_PATH_TO_FIXED_STUDENT_ANSWERS + "question_" + str(counter) + ".py")
                    with open(abs_path_to_python_fixed_answer_file, "w") as student_answer_python_file:
                        student_answer_python_file.write(student_answer_python_code)

                    # Get and run test module corresponding to question
                    test_module_name = "verification_tests.question_" + str(counter) + "_test"

                    test_module = importlib.import_module(test_module_name)

                    test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
                    unittest.TextTestRunner(verbosity=2).run(test_suite)

                    # Increment counter for next question loop
                    counter += 1

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


if __name__ == "__main__":
    # validate_answers_for_students_emails([
    #     "jean.ribes@insa-lyon.fr",
    #     "florian.bonnafond@insa-lyon.fr"
    # ])
    # validate_answers_for_students_emails([
    #     "bilel.saghrouchni@insa-lyon.fr"
    # ], interactive=True)
    validate_answers_for_students_emails([], interactive=True)
