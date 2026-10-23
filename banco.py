from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import TabelaNome

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/aula_teste"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def salvar_nome(nome, telefone):
    session = Session ()
    try:
        novo_registro = TabelaNome(nome=nome, telefone=int(telefone))
        session.add(novo_registro)
        session.commit()
    finally:
        session.close()

def listar_nome (pesquisa=""):
    session = Session()
    try:
        if pesquisa:
            return session.query(TabelaNome).filter(TabelaNome.nome.like(f"%{pesquisa}")).all()
        return session.query(TabelaNome).all()
    finally:
        session.close()

def excluir_nome(id_registro):
    session = Session ()
    try:
        registro = session.query(TabelaNome).filter_by(id=id_registro).first()
        if registro:
            session.delete(registro)
            session.commit()
            return True
        return False
    finally:
        session.close()

def telefone_numero(numero):
    session = Session ()
    try:
        novo_registro = TabelaNome(numero=numero)
        session.add(telefone_numero)
        session.commit()
    finally:
        session.close()
    