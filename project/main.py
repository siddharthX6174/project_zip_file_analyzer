from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from html import escape
import os
import json
from analyze_code import analyze_project  

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Mount the StaticFiles to serve CSS
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    return """
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>CodeDocu Analyzer</title>
            <link rel="stylesheet" href="/static/style.css?v=1.0">
        </head>
        <body class="page-shell">
            <main class="hero-card">
                <p class="eyebrow">FastAPI · Groq · Code Review</p>
                <h1>Code & README Analyzer</h1>
                <p class="lead">Upload a ZIP file and get a structured analysis for code quality, README clarity, and improvement suggestions.</p>
                <form action="/analyze" method="post" enctype="multipart/form-data" class="upload-form">
                    <label for="folder">Choose a ZIP file</label>
                    <input id="folder" name="folder" type="file" accept=".zip" required>
                    <button type="submit">Run Analysis</button>
                </form>
                <p class="hint">Make sure your ZIP includes at least one source file and a README.md.</p>
            </main>
        </body>
    </html>
    """

@app.post("/analyze")
async def analyze_code_folder(folder: UploadFile = File(...)):
    # Ensure the uploads directory exists
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    folder_name = os.path.basename(folder.filename)
    folder_path = os.path.join(UPLOADS_DIR, folder_name)

    # Save uploaded folder
    with open(folder_path, "wb") as f:
        f.write(await folder.read())

    try:
        # Call the analysis function
        analyze_project(folder_path)
    except RuntimeError as exc:
        if "GROQ_API_KEY is not set" in str(exc):
            return HTMLResponse(
                content="""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 24px;">
                        <h2>GROQ_API_KEY is not set</h2>
                        <p>Create or update <code>.env</code> in the <code>project</code> folder and add your Groq API key.</p>
                        <p>Example:</p>
                        <pre>GROQ_API_KEY=your_key_here\nGROQ_MODEL=llama-3.3-70b-versatile\nGROQ_BASE_URL=https://api.groq.com/openai/v1</pre>
                        <p><a href="/">Go back</a></p>
                    </body>
                </html>
                """,
                status_code=400,
            )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Generate and return the report display page
    return HTMLResponse(content=generate_report())

def generate_report():
    code_analysis_file = os.path.join(UPLOADS_DIR, 'extracted', 'code_analysis.json')
    readme_analysis_file = os.path.join(UPLOADS_DIR, 'extracted', 'readme_analysis.json')

    def format_score(value):
        try:
            score = float(value)
        except (TypeError, ValueError):
            return str(value)

        if 0 <= score <= 1:
            score *= 10

        if score.is_integer():
            return str(int(score))
        return f"{score:.1f}"

    def render_text(value):
        return escape(str(value))

    def render_feedback(value):
        if isinstance(value, dict):
            parts = []
            score_value = value.get('score', value.get('rating'))
            if score_value is not None:
                parts.append(f"<div class=\"score\">Score: {format_score(score_value)}</div>")
            feedback_value = value.get('feedback', value.get('summary'))
            if feedback_value is not None:
                parts.append(f"<div class=\"feedback\">{render_text(feedback_value)}</div>")
            for key, nested_value in value.items():
                if key not in {'score', 'rating', 'feedback', 'summary'}:
                    parts.append(
                        f"<div class=\"feedback\"><strong>{render_text(key.replace('_', ' ').title())}:</strong> {render_feedback(nested_value)}</div>"
                    )
            return "".join(parts)

        if isinstance(value, list):
            return "<ul>" + "".join(f"<li>{render_feedback(item)}</li>" for item in value) + "</ul>"

        return render_text(value)

    def render_section(title, payload, section_keys):
        section_html = [f"<h3>{render_text(title)}</h3>"]
        for key in section_keys:
            if key in payload:
                section_html.append(f"<h4>{render_text(key.replace('_', ' ').title())}</h4>")
                section_html.append(render_feedback(payload[key]))
                section_html.append("<hr>")
        return "".join(section_html)

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

        analysis = code_data.get('analysis', code_data)
        report_html += render_section("Code Analysis", analysis, ["style", "structure", "efficiency"])

        code_overall = code_data.get('overall_performance_score', code_data.get('overall_performance', {}).get('score'))
        if code_overall is not None:
            report_html += f"""
                <h3>Overall Performance Score</h3>
                <div class="score">Score: {format_score(code_overall)}</div>
                <hr>
            """

        code_suggestions = code_data.get('suggestions_for_improvement', code_data.get('suggestions'))
        if code_suggestions is not None:
            report_html += "<h3>Suggestions For Improvement</h3>"
            report_html += render_feedback(code_suggestions)
            report_html += "<hr>"

        improved_code = code_data.get('improved_code')
        if improved_code:
            report_html += "<h3>Improved Code</h3>"
            if isinstance(improved_code, str):
                report_html += f"<pre>{render_text(improved_code)}</pre><hr>"
            else:
                report_html += render_feedback(improved_code)
                report_html += "<hr>"
    except Exception as e:
        report_html += f"<p style='color:red;'>Error loading code analysis: {render_text(e)}</p>"

    report_html += "</div>"  # Close Code Analysis section

    try:
        # Read the README analysis JSON data
        with open(readme_analysis_file) as f:
            readme_data = json.load(f)

        report_html += "<div class=\"section\"><h2>README Analysis</h2>"

        readme_sections = {
            "Clarity": readme_data.get('clarity'),
            "Completeness": readme_data.get('completeness'),
            "Structure": readme_data.get('structure'),
        }
        for title, value in readme_sections.items():
            if value is not None:
                report_html += f"<h3>{render_text(title)}</h3>{render_feedback(value)}<hr>"

        readme_overall = readme_data.get('overall_performance_score', readme_data.get('overall', {}).get('score'))
        if readme_overall is not None:
            report_html += f"""
                <h3>Overall Performance Score</h3>
                <div class="score">Score: {format_score(readme_overall)}</div>
                <hr>
            """

        readme_suggestions = readme_data.get('suggestions_for_improvement', readme_data.get('suggestions'))
        if readme_suggestions is not None:
            report_html += "<h3>Suggestions For Improvement</h3>"
            report_html += render_feedback(readme_suggestions)
            report_html += "<hr>"

        report_html += "</div>"
        
    except Exception as e:
        report_html += f"<p style='color:red;'>Error loading README analysis: {render_text(e)}</p>"

    report_html += """
            <br>
            <a href="/">Go back</a>
        </div>
        </body>
    </html>
    """
    
    return report_html
