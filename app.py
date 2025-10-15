import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Get absolute path to the data directory and ensure it exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'questions.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AIzaSyDtoz4VTSxarpEvbswL0BZ_PmdUm4SS1h8'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class QuestionSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='question_set', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    explanation = db.Column(db.Text)
    question_set_id = db.Column(db.Integer, db.ForeignKey('question_set.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        subject = request.form.get('subject', 'General')
        topic = request.form.get('topic', 'Sample Topic')
        num_questions = int(request.form.get('num_questions', 5))
        # Dummy questions for demonstration
        questions = [f"Sample question {i+1} for {topic} ({subject})" for i in range(num_questions)]
        return render_template('results.html', questions=questions)
    return render_template('generate.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)
