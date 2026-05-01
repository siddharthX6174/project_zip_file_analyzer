from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from analyze_code import analyze_project  

app = FastAPI()

# Mount the StaticFiles to serve CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    return """
    <html>
        <head>
            <link rel="stylesheet" href="/static/style.css?v=1.0">
        </head>
        <body>
            <h2>Upload Project Folder</h2>
            <form action="/analyze" method="post" enctype="multipart/form-data">
                <input name="folder" type="file" accept=".zip" required>
                <input type="submit" value="Analyze">
            </form>
        </body>
    </html>
    """

@app.post("/analyze")
async def analyze_code_folder(folder: UploadFile = File(...)):
    # Ensure the uploads directory exists
    os.makedirs("./uploads", exist_ok=True)

    folder_path = f"./uploads/{folder.filename}"

    # Save uploaded folder
    with open(folder_path, "wb") as f:
        f.write(await folder.read())

    # Call the analysis function
    analyze_project(folder_path)

    # Generate and return the report display page
    return HTMLResponse(content=generate_report())

def generate_report():
    code_analysis_file = './uploads/extracted/code_analysis.json'
    readme_analysis_file = './uploads/extracted/readme_analysis.json'

    report_html = f"""
    <html>
        <head>
            <title>Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    background-color: #f9f9f9;
                }}
                .container {{
                    max-width: 800px;
                    margin: auto;
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                .section {{
                    margin-bottom: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #fafafa;
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                .score {{
                    font-weight: bold;
                    color: #28a745;  /* green */
                }}
                .feedback {{
                    font-style: italic;
                    color: #6c757d;  /* grey */
                }}
                pre {{
                    background-color: #ececec;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                }}
                a {{
                    text-decoration: none;
                    color: blue;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Analysis Report</h1>
                <div class="section">
                    <h2>Code Analysis</h2>
    """

    try:
        # Read the code analysis JSON data
        with open(code_analysis_file) as f:
            code_data = json.load(f)

        for category, result in code_data['analysis'].items():
            report_html += f"""
                <h3>{category.capitalize()}</h3>
                <div class="score">Score: {result['score']}</div>
                <div class="feedback">{result['feedback']}</div>
                <hr>
            """
    except Exception as e:
        report_html += f"<p style='color:red;'>Error loading code analysis: {e}</p>"

    report_html += "</div>"  # Close Code Analysis section

    try:
        # Read the README analysis JSON data
        with open(readme_analysis_file) as f:
            readme_data = json.load(f)

        report_html += """
            <div class="section">
                <h2>README Analysis</h2>
        """

        # Iterate through the README analysis data
        for key, value in readme_data.items():
            report_html += f"""
                <h3>{key.capitalize()}</h3>
                <div class="feedback">{str(value)[1:-1]}</div>
                <hr>
            """
        # Check if 'score' is a subkey in the current value
            if isinstance(value, dict) and 'score' in value:
                score = value['score']  # Extract the score
                report_html += f"""
                    <div class="score">Score: {score}</div>
                """
            report_html += "<hr>"
        report_html += """
            </div>
        """
        
    except Exception as e:
        report_html += f"<p style='color:red;'>Error loading README analysis: {e}</p>"

    report_html += """
            <br>
            <a href="/">Go back</a>
        </div>
        </body>
    </html>
    """
    
    return report_html
