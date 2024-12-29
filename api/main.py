from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, Float, MetaData, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

from typing import List

# 1. Configuração da URL do banco de dados PostgreSQL
DATABASE_URL = "postgresql://postgres.rsxdlivgzvkohtzahnbs:TheRootData1475@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"

# 2. Configuração do SQLAlchemy e criação do engine e da sessão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")


# 3. Base declarativa para o modelo
Base = declarative_base()

# 4. Definindo a tabela no banco de dados PostgreSQL usando SQLAlchemy
class TbPartidasTstModel(Base):
    __tablename__ = "tb_partidas_tst"
    id = Column(Integer, primary_key=True, index=True)
    versao = Column(String)
    win = Column(Boolean)
    nome = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    final_level = Column(Integer)
    stage = Column(Integer)
    relics_id = Column(JSON)
    statistics = Column(JSON)
    recipes = Column(JSON)
    itens = Column(JSON)
    nome_pc = Column(String)
    damage_taken = Column(Float)
    damage_healed = Column(Float)
    wave = Column(Integer)
    enemies_quantity = Column(Integer)

# 6. Pydantic models para validação
class SkillsStatisticsJson(BaseModel):
    startTime: str
    character: str
    damage: float
    damageBoss: float
    dps: float
    level: int

class RecipeJson(BaseModel):
    id: int
    level: int

class ItemJson(BaseModel):
    id: int
    level: int

class TbPartidasTst(BaseModel):
    versao: str
    win: bool
    nome: str
    start_time: str
    end_time: str
    final_level: int
    stage: int
    relics_id: List[int]
    statistics: List[SkillsStatisticsJson]
    recipes: List[RecipeJson]
    itens: List[ItemJson]
    nome_pc: str
    damage_taken: float
    damage_healed: float
    wave: int
    enemies_quantity: int

class TbPartidasTstResponse(TbPartidasTst):
    id: int

class TbPersonagensModel(Base):
    __tablename__ = "tb_personagens"
    id_personagem = Column(Integer, primary_key=True, index=True)
    nome_personagem = Column(String)

class TbPersonagens(BaseModel):
    id_personagem: int
    nome_personagem: str

class TbItensModel(Base):
    __tablename__ = "tb_itens"
    id_item = Column(Integer, primary_key=True, index=True)
    nome_item = Column(String)

class TbItens(BaseModel):
    id_item: int
    nome_item: str


class TbUsuariosModel(Base):
    __tablename__ = "tb_usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    login_usuario = Column(String)
    senha_usuario = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email_usuario = Column(String)
    
    def criar_hash_senha(self):
        self.senha_usuario = pwd_context.hash(self.senha_usuario)
    
    def verificar_senha(self, senha):
        return pwd_context.verify(senha, self.senha_usuario)

class TbUsuarios(BaseModel):
    login_usuario: str
    senha_usuario: str
    email_usuario: str

class TbUsuariosLogin(BaseModel):
    login_usuario: str
    senha_usuario: str

# 5. Criação da aplicação FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Dependência para acessar o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 7.1 Rota GET para consultar todas as partidas     
@app.get("/partidas/", response_model=List[TbPartidasTstResponse])
async def todas_partidas(
    db: Session = Depends(get_db),
    page: int = Query(1, gt=0, description="Número da página de resultados"),
    limit: int = Query(3000, gt=0, le=3000, description="Quantidade de resultados por página"),
):
    offset = (page - 1) * limit
    result = db.query(TbPartidasTstModel).limit(limit).offset(offset).all()
    return result

# 7.2 Rota GET para consultar em ordem por end_time e win = true
@app.get("/ranking/", response_model=List[TbPartidasTstResponse])
async def ranking_jogadores(db: Session = Depends(get_db)):
    result = (
        db.query(TbPartidasTstModel)
        .filter(TbPartidasTstModel.win == True)  
        .order_by(TbPartidasTstModel.end_time.asc()) 
        .limit(10)
        .all() 
    )
    return result

# 7.3 Rota GET para consultar em ordem por end_time e win = true com parametro de versão
@app.get("/ranking/{versao}", response_model=List[TbPartidasTstResponse])
async def ranking_jogadores_por_versao(
    versao: str, db: Session = Depends(get_db)
):
    result = (
        db.query(TbPartidasTstModel)
        .filter(TbPartidasTstModel.win == True, TbPartidasTstModel.versao == versao)
        .order_by(TbPartidasTstModel.end_time.asc())
        .limit(10)
        .all()
    )
    return result

# 7.4 Rota GET para consultar todos os personagens
@app.get("/personagens/", response_model=List[TbPersonagens])
async def todos_personagens(db: Session = Depends(get_db)):
    result = db.query(TbPersonagensModel).all()
    return result

# 7.5 Rota GET para consultar todos os itens
@app.get("/itens/", response_model=List[TbItens])
async def todos_itens(db: Session = Depends(get_db)):
    result = db.query(TbItensModel).all()
    return result 

# 8. Rota POST para criar uma nova entrada na tabela
@app.post("/partidas/")
async def criar_partida(partida: TbPartidasTst, db: Session = Depends(get_db)):
    db_partida = TbPartidasTstModel(
        versao=partida.versao,
        win=partida.win,
        nome=partida.nome,
        start_time=partida.start_time,
        end_time=partida.end_time,
        final_level=partida.final_level,
        stage=partida.stage,
        relics_id=partida.relics_id,
        statistics=jsonable_encoder(partida.statistics),    
        recipes=jsonable_encoder(partida.recipes),
        itens=jsonable_encoder(partida.itens),
        nome_pc=partida.nome_pc,
        damage_taken=partida.damage_taken,
        damage_healed=partida.damage_healed,
        wave=partida.wave,
        enemies_quantity=partida.enemies_quantity,
    )

    db.add(db_partida)
    db.commit()
    db.refresh(db_partida)

    return db_partida  

# 9. Rota POST para criar um novo usuário
@app.post("/criar_usuario/")
async def criar_usuario(usuario: TbUsuarios, db: Session = Depends(get_db)):
    db_usuario = TbUsuariosModel(
        login_usuario=usuario.login_usuario,
        senha_usuario=usuario.senha_usuario,
        email_usuario=usuario.email_usuario,
    )

    db_usuario.criar_hash_senha()

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)  

    return db_usuario

# 9.2 Rota POST para autenticar um usuário
@app.post("/login/")
async def autenticar_usuario(usuario: TbUsuariosLogin, db: Session = Depends(get_db)):
    
    db_usuario = db.query(TbUsuariosModel).filter_by(login_usuario=usuario.login_usuario).first()

    if db_usuario and db_usuario.verificar_senha(usuario.senha_usuario):
        return {"access_token": db_usuario.login_usuario, "token_type": "Bearer", "login": "Ok"}
    else:    
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
