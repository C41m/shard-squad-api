from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TbPersonagensModel(Base):
    __tablename__ = "tb_personagens"
    id_personagem = Column(Integer, primary_key=True, index=True)
    nome_personagem = Column(String)
