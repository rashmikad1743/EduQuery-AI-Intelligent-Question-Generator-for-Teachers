from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import DATABASE_PATH

Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def save_question(question, source):
    session = SessionLocal()
    q = Question(question=question, source=source)
    session.add(q)
    session.commit()
    session.close()

def get_all_questions():
    session = SessionLocal()
    questions = session.query(Question).order_by(Question.created_at.desc()).all()
    session.close()
    return [(q.question, q.source, q.created_at) for q in questions]