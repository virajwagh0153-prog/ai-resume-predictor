# AI Resume Predictor

A professional Diploma IT final-year project that analyzes a resume and predicts a suitable job role using a lightweight NLP/ML-style skill matching engine.

## Features
- Animated landing page
- Login and registration
- User dashboard
- Resume upload: PDF, DOCX, TXT
- Resume score
- Predicted job role
- Detected skills
- Missing skills
- Prediction history
- SQLite database
- Responsive modern UI
- Ready for deployment

## Run locally

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`

## Demo
Register a new account, then upload a resume.

## Note
This version uses transparent skill-based NLP scoring so it is easy to explain during a Diploma project viva. It can later be upgraded to a trained scikit-learn model using a labeled resume dataset.

## Deployment
Recommended: Render / Railway / PythonAnywhere. Before production, set a strong `app.secret_key`, use environment variables, disable Flask debug mode, and move to PostgreSQL.
