from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os, re, json, sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED = {"pdf", "docx", "txt"}

JOB_ROLES = {
    "Python Developer": ["python", "flask", "django", "sql", "git", "api"],
    "Data Analyst": ["python", "pandas", "numpy", "excel", "sql", "power bi", "tableau"],
    "Web Developer": ["html", "css", "javascript", "bootstrap", "react", "git"],
    "Software Developer": ["java", "python", "c++", "sql", "git", "oop"],
    "AI / ML Engineer": ["python", "machine learning", "scikit-learn", "tensorflow", "pandas", "numpy"],
    "Cyber Security Analyst": ["linux", "networking", "security", "python", "wireshark", "ethical hacking"]
}

def db():
    con = sqlite3.connect("resume_predictor.db")
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, filename TEXT,
        role TEXT, score INTEGER, skills TEXT, missing TEXT, created_at TEXT)""")
    con.commit(); con.close()

def extract_text(path):
    ext = path.rsplit(".",1)[-1].lower()
    if ext == "txt":
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    if ext == "pdf":
        try:
            from pypdf import PdfReader
            return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
        except Exception:
            return ""
    if ext == "docx":
        try:
            from docx import Document
            return "\n".join(p.text for p in Document(path).paragraphs)
        except Exception:
            return ""
    return ""

def analyze(text):
    t = text.lower()
    scores = {}
    matched = {}
    for role, skills in JOB_ROLES.items():
        found = [s for s in skills if s in t]
        matched[role] = found
        scores[role] = round(len(found)/len(skills)*100)
    role = max(scores, key=scores.get)
    found = matched[role]
    missing = [s for s in JOB_ROLES[role] if s not in found]
    # simple confidence/score with a small bonus for resume completeness
    sections = sum(x in t for x in ["education","experience","project","skills","contact","email"])
    score = min(98, round(scores[role]*0.8 + sections/6*20))
    return role, score, found, missing

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        con=db()
        user=con.execute("SELECT * FROM users WHERE email=? AND password=?",
                         (request.form["email"], request.form["password"])).fetchone()
        con.close()
        if user:
            session["user_id"]=user["id"]; session["name"]=user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            con=db()
            con.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                        (request.form["name"],request.form["email"],request.form["password"]))
            con.commit(); con.close()
            flash("Account created. Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("login"))
    con=db()
    rows=con.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY id DESC",(session["user_id"],)).fetchall()
    con.close()
    return render_template("dashboard.html", rows=rows, name=session["name"])

@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session: return redirect(url_for("login"))
    f=request.files.get("resume")
    if not f or not f.filename or "." not in f.filename or f.filename.rsplit(".",1)[-1].lower() not in ALLOWED:
        flash("Please upload a PDF, DOCX or TXT resume.")
        return redirect(url_for("dashboard"))
    filename=secure_filename(f.filename)
    path=os.path.join(app.config["UPLOAD_FOLDER"],filename)
    f.save(path)
    text=extract_text(path)
    if not text.strip():
        text = f.filename.replace("_"," ").replace("-"," ")
    role,score,skills,missing=analyze(text)
    con=db()
    con.execute("""INSERT INTO predictions(user_id,filename,role,score,skills,missing,created_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (session["user_id"],filename,role,score,json.dumps(skills),json.dumps(missing),
                 datetime.now().strftime("%d %b %Y, %I:%M %p")))
    con.commit(); con.close()
    return render_template("result.html", role=role, score=score, skills=skills, missing=missing)

init_db()
if __name__=="__main__":
    app.run(debug=True)
