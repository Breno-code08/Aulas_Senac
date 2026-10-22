from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TabelaNome (Base):
    __tablename__= "alunos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100))