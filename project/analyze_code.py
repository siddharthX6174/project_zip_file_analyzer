import json
import os
import re
import shutil
import zipfile

from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()


def get_client():
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set")
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def generate_json_response(prompt):
    client = get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "Return only valid JSON with no markdown fences."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    response_text = response.choices[0].message.content or ""
    response_text = response_text.strip()
    response_text = re.sub(r'^```json\s*', '', response_text, flags=re.IGNORECASE)
    response_text = re.sub(r'^```\s*', '', response_text)
    response_text = re.sub(r'\s*```$', '', response_text)

    json_start = response_text.find('{')
    json_end = response_text.rfind('}')
    if json_start != -1 and json_end != -1 and json_end > json_start:
        response_text = response_text[json_start:json_end + 1]

    try:
        return json.loads(response_text, strict=False)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Groq returned invalid JSON: {exc}") from exc

def analyze_code(file_path):
    with open(file_path, 'r') as file:
        code_content = file.read()

    prompt = (
        "Analyze the following code and return ONLY valid JSON with this exact shape: "
        "{\"analysis\": {\"style\": {\"score\": 1, \"feedback\": \"...\"}, "
        "\"structure\": {\"score\": 1, \"feedback\": \"...\"}, "
        "\"efficiency\": {\"score\": 1, \"feedback\": \"...\"}}, "
        "\"overall_performance_score\": 1, "
        "\"suggestions_for_improvement\": [\"...\"]}. "
        "Use integer scores from 1 to 10 only. Keep feedback concise. "
        "Do not include improved code. Do not wrap the JSON in markdown fences. "
        "Use only double quotes for JSON strings.\n"
        f"Code:\n{code_content}"
    )

    return generate_json_response(prompt)

def analyze_readme(file_path):
    with open(file_path, 'r') as file:
        readme_content = file.read()

    prompt = (
        "Analyze the following README.md file and return ONLY valid JSON with this exact shape: "
        "{\"clarity\": {\"score\": 1, \"feedback\": \"...\"}, "
        "\"completeness\": {\"score\": 1, \"feedback\": \"...\"}, "
        "\"structure\": {\"score\": 1, \"feedback\": \"...\"}, "
        "\"overall_performance_score\": 1, "
        "\"suggestions_for_improvement\": [\"...\"]}. "
        "Use integer scores from 1 to 10 only. Keep feedback concise. "
        "Do not include improved code. Do not wrap the JSON in markdown fences. "
        "Use only double quotes for JSON strings.\n"
        f"README content:\n{readme_content}"
    )

    return generate_json_response(prompt)

def save_json_to_file(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def safe_extract_zip(zip_ref, target_dir):
    for member in zip_ref.infolist():
        member_path = os.path.abspath(os.path.join(target_dir, member.filename))
        if not member_path.startswith(os.path.abspath(target_dir) + os.sep):
            raise ValueError(f"Unsafe file path in zip archive: {member.filename}")
    zip_ref.extractall(target_dir)

def analyze_project(folder_path):
    # If your input is a zip file, extract it first
    uploads_dir = os.path.join(BASE_DIR, "uploads")
    extracted_path = os.path.join(uploads_dir, "extracted")
    if os.path.exists(extracted_path):
        shutil.rmtree(extracted_path)
    os.makedirs(extracted_path, exist_ok=True)

    with zipfile.ZipFile(folder_path, 'r') as zip_ref:
        safe_extract_zip(zip_ref, extracted_path)

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
