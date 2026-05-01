# Intern Assignment checker - GenAI & FastAPI Based Code & Documentation Analyzer

## Overview

This project is a FastAPI application leveraging the power of the Gemini's Generative AI API that allows users to upload a project folder (in ZIP format) for code and README analysis. The application evaluates the quality of the code, generates improved code suggestions, and assesses the quality of the README documentation. The results are presented through a web interface, making it easy for developers to understand the strengths and weaknesses of their projects.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Code Analysis](#code-analysis)
- [README Analysis](#readme-analysis)
- [Contributing](#contributing)
- [Contact](#contact)
- [Webapp Screenshots](#webapp-screenshots)

## Requirements 

- **Python**: Version 3.8 or higher
- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running the FastAPI application
- **Gemini API** : Gemini's Generative AI API for code & documentation analysis

## Installation

1. **Clone the Repository**

   Open your terminal and clone the repository:

   ```bash
   git clone https://github.com/anou1234/Fastapi_code_docu_analyzer.git
   cd my_fastapi_project
   ```

2. **Set up a Virtual Environment**

   Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies**

   Use `pip` to install the required packages:

   ```bash
   pip install -r requirements.txt
   ```


## Usage

1. **Start the Application**

   Run the FastAPI application using Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

2. **Access the Application**

   Open your web browser and navigate to:

   ```
   http://127.0.0.1:8000
   ```

3. **Upload a Project Folder**

   Use the web interface to upload a ZIP file containing the project you wish to analyze.

## Code Analysis

The application analyzes the submitted code for various quality metrics, including but not limited to:

- **Code Complexity**: Evaluates the complexity of the code to ensure maintainability.
- **Readability**: Checks the readability and structure of the code.
- **Improved Code Suggestions**: Provides suggestions for improved code practices and patterns.

## README Analysis

The application also evaluates the README documentation to ensure it is informative and well-structured. The analysis includes:

- Clarity of project overview
- Proper usage instructions
- Dependencies and installation steps
- Contribution guidelines
![image]()

## Contributing

Contributions are welcome! If you'd like to help improve this project, please follow these steps:

1. **Fork the Repository**: Create your copy of the repository on GitHub.
2. **Create a Branch**: Work on your feature or fix:
3. **Commit Your Changes**: Keep your commits clear and concise.
4. **Push to Your Branch**: 
5. **Submit a Pull Request**: Share your changes with the main project.
## Webapp Screenshots
<img src="https://github.com/user-attachments/assets/eb0ef7d7-7423-4912-a897-b8e6046f5941" alt="Screenshot 2024-09-15 214027" width="600" height="300">
<img src="https://github.com/user-attachments/assets/d006fd9c-f31d-496c-ab7a-23e7886748d9" alt="Screenshot 2024-09-15 214125" width="600" height="300">
<img src="https://github.com/user-attachments/assets/84786eb4-f52d-4e01-b18c-cf9cd15121c9" alt="Screenshot 2024-09-15 214139" width="600" height="300">

## Contact

- **Author**: Anoushka Srivastava
- **Email**: anoushkathegreat28@gmail.com/anoushka.srivastava.21cse@bmu.edu.in
- **GitHub**: [anou1234](https://github.com/anou1234)
