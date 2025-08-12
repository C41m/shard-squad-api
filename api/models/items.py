from sqlalchemy import Column, Integer, String, Boolean, Float, Numeric
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TbItensModel(Base):
    __tablename__ = "tb_itens"
    id_item = Column(Integer, primary_key=True, index=True)
    nome_item = Column(String)
