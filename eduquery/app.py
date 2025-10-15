from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from io import BytesIO

# RAG Components
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/questions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db = SQLAlchemy(app)

# Database Models (same as before)
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
    bloom_level = db.Column(db.String(50))
    source_context = db.Column(db.Text)  # RAG: Source content
    question_set_id = db.Column(db.Integer, db.ForeignKey('question_set.id'), nullable=False)

# Create tables
with app.app_context():
    os.makedirs('data', exist_ok=True)
    db.create_all()


# ==================== RAG IMPLEMENTATION ====================

class KnowledgeBase:
    """
    Knowledge Base for storing educational content
    In production, this would be a vector database like Pinecone, Weaviate, or FAISS
    """
    
    def __init__(self):
        # Sample educational content (in real app, load from files/database)
        self.knowledge = {
            'Mathematics': {
                'Algebra': [
                    "Algebra is a branch of mathematics dealing with symbols and the rules for manipulating those symbols. Variables represent unknown quantities, and equations express relationships between these variables.",
                    "Quadratic equations are polynomial equations of degree two. The standard form is ax² + bx + c = 0, where a ≠ 0. Solutions can be found using factoring, completing the square, or the quadratic formula.",
                    "Linear equations represent straight lines when graphed. They have the form y = mx + b, where m is the slope and b is the y-intercept.",
                    "Systems of equations involve multiple equations with multiple variables. Solutions can be found using substitution, elimination, or graphical methods."
                ],
                'Geometry': [
                    "Geometry studies shapes, sizes, and spatial relationships. Basic shapes include triangles, circles, rectangles, and polygons.",
                    "The Pythagorean theorem states that in a right triangle, a² + b² = c², where c is the hypotenuse.",
                    "Area formulas vary by shape: rectangles use length × width, triangles use ½ × base × height, and circles use πr²."
                ]
            },
            'Biology': {
                'Cell Structure': [
                    "Cells are the basic unit of life. All living organisms are made of one or more cells. The cell theory states that all cells come from pre-existing cells.",
                    "Prokaryotic cells lack a nucleus and membrane-bound organelles. They are typically smaller and simpler than eukaryotic cells. Bacteria are prokaryotes.",
                    "Eukaryotic cells have a nucleus containing DNA and various membrane-bound organelles. Plant and animal cells are eukaryotic.",
                    "The cell membrane is a semi-permeable barrier controlling what enters and exits the cell. It consists of a phospholipid bilayer with embedded proteins.",
                    "Mitochondria are the powerhouses of the cell, producing ATP through cellular respiration. Plant cells also have chloroplasts for photosynthesis."
                ],
                'Photosynthesis': [
                    "Photosynthesis is the process by which plants convert light energy into chemical energy stored in glucose. The equation is: 6CO2 + 6H2O + light → C6H12O6 + 6O2.",
                    "Chlorophyll is the green pigment in chloroplasts that captures light energy. It primarily absorbs red and blue light, reflecting green.",
                    "The light-dependent reactions occur in the thylakoid membranes, producing ATP and NADPH. Water is split, releasing oxygen as a byproduct.",
                    "The Calvin cycle (light-independent reactions) uses ATP and NADPH to fix carbon dioxide into glucose in the stroma."
                ]
            },
            'Physics': {
                'Motion': [
                    "Newton's First Law states that an object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force.",
                    "Newton's Second Law: F = ma, where force equals mass times acceleration. This explains how forces cause objects to accelerate.",
                    "Velocity is speed with direction. Acceleration is the rate of change of velocity. Uniform motion means constant velocity."
                ]
            },
            'Computer Science': {
                'Python Programming': [
                    "Python is a high-level, interpreted programming language known for its readable syntax and versatility. It uses indentation to define code blocks.",
                    "Variables in Python don't need type declarations. Python dynamically determines the type based on the assigned value.",
                    "Functions are defined using the 'def' keyword. They encapsulate reusable code and can accept parameters and return values.",
                    "Lists are mutable ordered collections, while tuples are immutable. Dictionaries store key-value pairs for efficient data lookup."
                ]
            }
        }
        
        # Initialize embedding model (lightweight)
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Pre-compute embeddings for faster retrieval
        self.embeddings_cache = {}
        self._build_embeddings()
    
    def _build_embeddings(self):
        """Pre-compute embeddings for all knowledge"""
        print("Building knowledge base embeddings...")
        for subject, topics in self.knowledge.items():
            for topic, contents in topics.items():
                key = f"{subject}_{topic}"
                self.embeddings_cache[key] = self.embedding_model.encode(contents)
        print("✓ Knowledge base ready!")
    
    def retrieve_context(self, subject, topic, query=None, top_k=3):
        """
        Retrieve relevant context using RAG
        """
        key = f"{subject}_{topic}"
        
        # Check if we have content for this subject-topic
        if subject not in self.knowledge or topic not in self.knowledge[subject]:
            # Return generic context if not found
            return [f"General information about {topic} in {subject}."]
        
        contents = self.knowledge[subject][topic]
        
        # If no specific query, return all content
        if not query:
            return contents[:top_k]
        
        # Use semantic search to find most relevant content
        query_embedding = self.embedding_model.encode([query])
        content_embeddings = self.embeddings_cache[key]
        
        # Calculate similarity scores
        similarities = cosine_similarity(query_embedding, content_embeddings)[0]
        
        # Get top-k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [contents[i] for i in top_indices]


class RAGQuestionGenerator:
    """
    Question Generator with RAG (Retrieval-Augmented Generation)
    """
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.bloom_taxonomy = {
            'remember': ['What is', 'Define', 'List', 'Identify', 'Name', 'State', 'Recall'],
            'understand': ['Explain', 'Describe', 'Summarize', 'Interpret', 'Compare', 'Discuss'],
            'apply': ['Apply', 'Demonstrate', 'Calculate', 'Solve', 'Use', 'Implement'],
            'analyze': ['Analyze', 'Examine', 'Differentiate', 'Investigate', 'Compare', 'Contrast'],
            'evaluate': ['Evaluate', 'Justify', 'Critique', 'Assess', 'Argue', 'Judge'],
            'create': ['Design', 'Construct', 'Develop', 'Create', 'Formulate', 'Propose']
        }
    
    def generate_questions(self, subject, topic, difficulty, question_type, num_questions):
        """Generate questions using RAG approach"""
        questions = []
        
        # Retrieve relevant context from knowledge base
        context_docs = self.kb.retrieve_context(subject, topic, top_k=num_questions)
        
        for i in range(num_questions):
            # Get relevant context for this question
            context = context_docs[i % len(context_docs)]
            
            if question_type == 'mcq':
                question = self.generate_mcq_with_rag(subject, topic, difficulty, context, i)
            elif question_type == 'short_answer':
                question = self.generate_short_answer_with_rag(subject, topic, difficulty, context, i)
            elif question_type == 'true_false':
                question = self.generate_true_false_with_rag(subject, topic, difficulty, context, i)
            elif question_type == 'essay':
                question = self.generate_essay_with_rag(subject, topic, difficulty, context, i)
            else:
                question = self.generate_mixed_with_rag(subject, topic, difficulty, context, i)
            
            questions.append(question)
        
        return questions
    
    def generate_mcq_with_rag(self, subject, topic, difficulty, context, index):
        """Generate MCQ based on retrieved context"""
        bloom_level = self.get_bloom_level(difficulty)
        starter = self.bloom_taxonomy[bloom_level][index % len(self.bloom_taxonomy[bloom_level])]
        
        # Extract key concepts from context
        sentences = context.split('.')
        key_concept = sentences[0].strip() if sentences else context[:100]
        
        question_text = f"{starter} the following about {topic}: {key_concept[:80]}..."
        
        # Generate options based on context
        options = [
            key_concept,  # Correct answer
            f"An alternative interpretation of {topic}",
            f"A common misconception about {topic}",
            f"An unrelated concept in {subject}"
        ]
        
        return {
            'question_text': question_text,
            'options': json.dumps(options),
            'correct_answer': options[0],
            'explanation': f"Based on the principle: {context[:150]}...",
            'bloom_level': bloom_level,
            'source_context': context
        }
    
    def generate_short_answer_with_rag(self, subject, topic, difficulty, context, index):
        """Generate short answer based on context"""
        bloom_level = self.get_bloom_level(difficulty)
        starter = self.bloom_taxonomy[bloom_level][index % len(self.bloom_taxonomy[bloom_level])]
        
        question_text = f"{starter} the concept discussed in {topic} regarding: {context[:100]}..."
        
        return {
            'question_text': question_text,
            'options': None,
            'correct_answer': f"Answer should include: {context[:200]}",
            'explanation': f"This requires understanding of: {context}",
            'bloom_level': bloom_level,
            'source_context': context
        }
    
    def generate_true_false_with_rag(self, subject, topic, difficulty, context, index):
        """Generate True/False based on context"""
        bloom_level = self.get_bloom_level(difficulty)
        
        # Extract a factual statement from context
        statement = context.split('.')[0] if '.' in context else context[:100]
        
        question_text = f"{statement}. (True/False)"
        
        return {
            'question_text': question_text,
            'options': json.dumps(['True', 'False']),
            'correct_answer': 'True',
            'explanation': f"This is true based on: {context}",
            'bloom_level': bloom_level,
            'source_context': context
        }
    
    def generate_essay_with_rag(self, subject, topic, difficulty, context, index):
        """Generate essay question based on context"""
        bloom_level = 'evaluate' if difficulty in ['hard', 'expert'] else 'analyze'
        starter = self.bloom_taxonomy[bloom_level][index % len(self.bloom_taxonomy[bloom_level])]
        
        question_text = f"{starter} the following concept in {topic}: {context[:150]}... Provide detailed examples and analysis."
        
        return {
            'question_text': question_text,
            'options': None,
            'correct_answer': f"Comprehensive response should cover: {context}",
            'explanation': f"This requires deep analysis of: {context}",
            'bloom_level': bloom_level,
            'source_context': context
        }
    
    def generate_mixed_with_rag(self, subject, topic, difficulty, context, index):
        """Generate mixed type questions"""
        types = ['mcq', 'short_answer', 'true_false']
        selected_type = types[index % len(types)]
        
        if selected_type == 'mcq':
            return self.generate_mcq_with_rag(subject, topic, difficulty, context, index)
        elif selected_type == 'short_answer':
            return self.generate_short_answer_with_rag(subject, topic, difficulty, context, index)
        else:
            return self.generate_true_false_with_rag(subject, topic, difficulty, context, index)
    
    def get_bloom_level(self, difficulty):
        """Map difficulty to Bloom's taxonomy"""
        mapping = {
            'easy': 'remember',
            'medium': 'understand',
            'hard': 'apply',
            'expert': 'analyze'
        }
        return mapping.get(difficulty, 'understand')


# Initialize RAG components
print("\n" + "="*60)
print("INITIALIZING RAG-ENHANCED QUESTION GENERATOR")
print("="*60)
knowledge_base = KnowledgeBase()
generator = RAGQuestionGenerator(knowledge_base)
print("="*60 + "\n")


# Custom Jinja2 filter
@app.template_filter('from_json')
def from_json_filter(value):
    if value:
        return json.loads(value)
    return []


# Routes (same as before, just using RAG generator)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            subject = request.form.get('subject')
            topic = request.form.get('topic')
            difficulty = request.form.get('difficulty')
            question_type = request.form.get('question_type')
            num_questions = int(request.form.get('num_questions'))
            
            if not all([title, subject, topic, difficulty, question_type, num_questions]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('generate'))
            
            if num_questions < 1 or num_questions > 20:
                flash('Number of questions must be between 1 and 20', 'danger')
                return redirect(url_for('generate'))
            
            # Generate questions using RAG
            questions = generator.generate_questions(
                subject, topic, difficulty, question_type, num_questions
            )
            
            # Save to database
            question_set = QuestionSet(
                title=title,
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                num_questions=num_questions
            )
            db.session.add(question_set)
            db.session.flush()
            
            for q_data in questions:
                question = Question(
                    question_text=q_data['question_text'],
                    options=q_data['options'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation'],
                    bloom_level=q_data['bloom_level'],
                    source_context=q_data.get('source_context'),
                    question_set_id=question_set.id
                )
                db.session.add(question)
            
            db.session.commit()
            
            flash('Questions generated successfully using RAG!', 'success')
            return redirect(url_for('results', question_set_id=question_set.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error generating questions: {str(e)}', 'danger')
            return redirect(url_for('generate'))
    
    return render_template('generate.html')

@app.route('/results/<int:question_set_id>')
def results(question_set_id):
    question_set = QuestionSet.query.get_or_404(question_set_id)
    return render_template('results.html', question_set=question_set)

@app.route('/history')
def history():
    question_sets = QuestionSet.query.order_by(QuestionSet.created_at.desc()).all()
    return render_template('history.html', question_sets=question_sets)

@app.route('/delete/<int:question_set_id>', methods=['POST'])
def delete_question_set(question_set_id):
    question_set = QuestionSet.query.get_or_404(question_set_id)
    db.session.delete(question_set)
    db.session.commit()
    flash('Question set deleted successfully!', 'success')
    return redirect(url_for('history'))

@app.route('/export/<int:question_set_id>')
def export_questions(question_set_id):
    question_set = QuestionSet.query.get_or_404(question_set_id)
    
    export_data = {
        'title': question_set.title,
        'subject': question_set.subject,
        'topic': question_set.topic,
        'difficulty': question_set.difficulty,
        'created_at': question_set.created_at.isoformat(),
        'questions': []
    }
    
    for q in question_set.questions:
        question_data = {
            'question': q.question_text,
            'options': json.loads(q.options) if q.options else None,
            'correct_answer': q.correct_answer,
            'explanation': q.explanation,
            'bloom_level': q.bloom_level,
            'source_context': q.source_context
        }
        export_data['questions'].append(question_data)
    
    json_str = json.dumps(export_data, indent=2)
    file_obj = BytesIO(json_str.encode('utf-8'))
    file_obj.seek(0)
    
    filename = f"{question_set.title.replace(' ', '_')}.json"
    
    return send_file(
        file_obj,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)