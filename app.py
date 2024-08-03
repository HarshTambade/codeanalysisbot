from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import ast
import io
import contextlib
import random

app = Flask(__name__)

def load_datasets():
    datasets = {}
    try:
        easy_df = pd.read_excel('Easy Questions.xlsx')
        medium_df = pd.read_excel('Medium Questions.xlsx')
        hard_df = pd.read_excel('Hard Questions.xlsx')

        datasets['Easy'] = easy_df['Questions'].tolist()
        datasets['Medium'] = medium_df['Questions'].tolist()
        datasets['Hard'] = hard_df['Questions'].tolist()
    except FileNotFoundError as e:
        print(f"Error loading file: {e}")
        exit(1)

    return datasets

datasets = load_datasets()

def analyze_code(user_code, expected_output):
    analysis_results = {
        "syntax_valid": False,
        "function_check": "",
        "logic_check": "",
        "quality_check": "",
        "score": 0
    }

    # Check syntax validity
    try:
        ast.parse(user_code)
        analysis_results["syntax_valid"] = True
    except SyntaxError as e:
        analysis_results["function_check"] = f"Syntax error: {e}"
        return analysis_results

    # Check for function definitions
    tree = ast.parse(user_code)
    function_count = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
    if function_count == 0:
        analysis_results["function_check"] = "No functions defined."
        analysis_results["score"] = 2
    else:
        analysis_results["function_check"] = f"Functions defined: {function_count}"

    # Check logic by executing the code
    logic_feedback, logic_score = check_logic(user_code, expected_output)
    analysis_results["logic_check"] = logic_feedback

    # Assess code quality
    quality_score, quality_feedback = assess_code_quality(user_code)
    analysis_results["quality_check"] = quality_feedback
    analysis_results["score"] = logic_score + quality_score

    # Ensure the score does not exceed 10
    analysis_results["score"] = min(analysis_results["score"], 10)

    return analysis_results

def check_logic(user_code, expected_output):
    try:
        exec_globals = {}
        exec(user_code, exec_globals)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            if 'main' in exec_globals:
                exec_globals['main']()
            else:
                return "Function 'main' not defined.", 0

        user_output = output.getvalue().strip()
        if user_output == expected_output:
            return "Correct logic", 5
        else:
            return f"Incorrect logic. Expected output: '{expected_output}', but got: '{user_output}'", 3
    except Exception as e:
        return f"Runtime error: {e}", 0

def assess_code_quality(user_code):
    quality_score = 0
    feedback = []

    lines = user_code.splitlines()
    for line in lines:
        if 'print(' in line:
            feedback.append("Avoid using print statements in the final code.")
        if len(line) > 80:
            feedback.append("Consider breaking long lines into shorter ones.")
        if 'import' in line and len(line.split()) > 1 and line.split()[1] not in ['sys', 'math', 'random']:
            feedback.append("Avoid unnecessary imports.")
    
    if len(feedback) == 0:
        quality_score = 3
    elif len(feedback) <= 2:
        quality_score = 2
    else:
        quality_score = 1

    return quality_score, "\n".join(feedback)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/get_question', methods=['GET'])
def get_question():
    difficulty = request.args.get('difficulty')
    if difficulty not in datasets:
        return jsonify({"error": "Invalid difficulty level"}), 400

    questions = datasets[difficulty]
    if not questions:
        return jsonify({"error": "No questions available"}), 400

    question = random.choice(questions)
    return jsonify({"question": question})

@app.route('/analyze_code', methods=['POST'])
def analyze_code_endpoint():
    data = request.get_json()
    difficulty = data['difficulty']
    user_code = data['userCode']
    expected_output = data['expected_output']

    analysis_results = analyze_code(user_code, expected_output)
    return jsonify(analysis_results)

if __name__ == '__main__':
    app.run(debug=True)
