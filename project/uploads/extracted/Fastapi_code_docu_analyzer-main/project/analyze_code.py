import google.generativeai as genai
import os
import json
import zipfile
import re

genai.configure(api_key='')  # Replace with your actual API key
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_code(file_path):
    with open(file_path, 'r') as file:
        code_content = file.read()

    prompt = (f"Analyze the following code and provide feedback on its style, structure, and efficiency. "
              f"Give each aspect a performance score from 1 to 10, where 10 is excellent. "
              f"Then, compute an overall performance score. Additionally, offer suggestions for improvement. "
              f"Finally, provide the improved code. Format the entire response as a JSON object:\n"
              f"{code_content}")

    response = model.generate_content(prompt)
    response_text = response.text.strip()
    response_text = re.sub(r'^```json', '', response_text)
    response_text = re.sub(r'```$', '', response_text).strip()

    structured_output = json.loads(response_text)
    return structured_output

def analyze_readme(file_path):
    with open(file_path, 'r') as file:
        readme_content = file.read()

    prompt = (f"Analyze the following README.md file and provide feedback on its clarity, completeness, and structure. "
              f"Give each aspect a performance score from 1 to 10, where 10 is excellent. "
              f"Then, compute an overall performance score. Additionally, offer suggestions for improvement. "
              f"Format the entire response as a JSON object:\n"
              f"{readme_content}")

    response = model.generate_content(prompt)
    response_text = response.text.strip()
    response_text = re.sub(r'^```json', '', response_text)
    response_text = re.sub(r'```$', '', response_text).strip()

    structured_output = json.loads(response_text)
    return structured_output

def save_json_to_file(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def analyze_project(folder_path):
    # If your input is a zip file, extract it first
    extracted_path = f"./uploads/extracted"
    os.makedirs(extracted_path, exist_ok=True)

    with zipfile.ZipFile(folder_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_path)

    # Search for files to analyze
    code_file_path = None
    readme_file_path = None

    # Search for .py files
    for root, dirs, files in os.walk(extracted_path):
        for file in files:
            if file.endswith(('.py', '.java', '.js', '.cpp', '.c', '.html')):
                code_file_path = os.path.join(root, file)
                break
        if code_file_path:
            break

    # Search for README.md file
    for root, dirs, files in os.walk(extracted_path):
        for file in files:
            if file.lower() == 'readme.md':
                readme_file_path = os.path.join(root, file)
                break
        if readme_file_path:
            break

    if not code_file_path:
        raise FileNotFoundError("No code file found in the uploaded folder.")
    if not readme_file_path:
        raise FileNotFoundError("No README.md file found in the uploaded folder.")

    code_output_file_path = os.path.join(extracted_path, 'code_analysis.json')
    readme_output_file_path = os.path.join(extracted_path, 'readme_analysis.json')

    # Analyze the code and get structured JSON output
    code_output = analyze_code(code_file_path)
    save_json_to_file(code_output, code_output_file_path)

    # Analyze the README.md and get structured JSON output
    readme_output = analyze_readme(readme_file_path)
    save_json_to_file(readme_output, readme_output_file_path)

    print(f"Code analysis saved to {code_output_file_path}")
    print(f"README analysis saved to {readme_output_file_path}")
