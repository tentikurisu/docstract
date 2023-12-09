import ast
import os
import inspect
import subprocess
import astunparse

def get_function_explanation(file_path, function_name):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            docstring = ast.get_docstring(node)
            if docstring:
                return docstring
            else:
                # If no docstring, get function signature and types
                signature = astunparse.unparse(node)
                types_info = get_function_types(file_path, function_name)
                return f"{signature}\n\n{types_info}"

    return ''

def get_function_types(file_path, function_name):
    try:
        pylint_result = subprocess.run(['pylint', file_path, '--disable=all', '--enable=pylint.extensions.docparams', '--output-format=json'], capture_output=True, text=True)
        pylint_output = pylint_result.stdout
        mypy_result = subprocess.run(['mypy', file_path, '--show-error-codes'], capture_output=True, text=True)
    except FileNotFoundError:
        return "Pylint or MyPy not found. Please make sure they are installed."

    types_info = f"Pylint Output:\n{pylint_output}\n\nMypy Output:\n{mypy_result.stdout}"

    return types_info

def process_folder(folder_path, doc_file_path):
    with open(doc_file_path, 'w') as doc_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    doc_file.write(f"\n# Function Documentation\n\n")
                    process_file(file_path, doc_file)

def process_file(file_path, doc_file):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            explanation = get_function_explanation(file_path, function_name)
            doc_file.write(f"## {file_path}:{function_name}\n\n```python\n{explanation}\n```\n\n")

def process_function(node, doc_file, file_path):  # Pass file_path as a parameter
    function_name = node.name
    explanation = get_function_explanation(file_path, function_name)
    doc_file.write(f"## {file_path}:{function_name}\n\n```python\n{explanation}\n```\n\n")

def main():
    folder_path = input("Enter the folder path: ")
    doc_file_path = input("Enter the doc file path: ")
    process_folder(folder_path, doc_file_path)

if __name__ == "__main__":
    main()