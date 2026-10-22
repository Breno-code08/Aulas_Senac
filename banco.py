from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import TabelaNome

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/aula_teste"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def salvar_nome(nome):
    session = Session ()
    try:
        novo_registro = TabelaNome(nome=nome)
        session.add(novo_registro)
        session.commit()
    finally:
        session.close()