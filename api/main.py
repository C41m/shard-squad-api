from sqlalchemy import *
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
from sqlalchemy.orm import aliased
from typing import List

from models.partidas import TbPartidasTstModel
from models.personagens import TbPersonagensModel
from models.items import TbItensModel

from schemas.partidas import TbPartidasTst
from schemas.personagens import TbPersonagens
from schemas.items import TbItens

# 1. Configuração da URL do banco de dados PostgreSQL
DATABASE_URL = "postgresql://postgres.rsxdlivgzvkohtzahnbs:TheRootData1475@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"

# 2. Configuração do SQLAlchemy e criação do engine e da sessão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")


# 3. Base declarativa para o modelo
Base = declarative_base()

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


class TbPartidasTstResponse(TbPartidasTst):
    id: int


# 7.1 Rota GET para consultar todas as partidas
@app.get("/partidas/", response_model=List[TbPartidasTstResponse])
async def todas_partidas(
    db: Session = Depends(get_db),
    page: int = Query(1, gt=0, description="Número da página de resultados"),
    limit: int = Query(
        3000, gt=0, le=3000, description="Quantidade de resultados por página"
    ),
):
    offset = (page - 1) * limit
    result = db.query(TbPartidasTstModel).limit(limit).offset(offset).all()
    return result


# 7.2 Rota GET para consultar em ordem por end_time e win = true
@app.get("/ranking/", response_model=List[TbPartidasTstResponse])
async def ranking_jogadores(db: Session = Depends(get_db)):
    subquery = (
        db.query(
            TbPartidasTstModel.steam_id,
            func.min(TbPartidasTstModel.end_time).label("menor_tempo"),
        )
        .filter(TbPartidasTstModel.win == True)
        .group_by(TbPartidasTstModel.steam_id)
        .subquery()
    )

    alias_partida = aliased(TbPartidasTstModel)

    result = (
        db.query(alias_partida)
        .join(
            subquery,
            (alias_partida.steam_id == subquery.c.steam_id)
            & (alias_partida.end_time == subquery.c.menor_tempo),
        )
        .order_by(alias_partida.end_time.asc())
        .limit(10)
        .all()
    )
    return result


# 7.3 Rota GET para consultar em ordem por end_time e win = true com parametro de versão
@app.get("/ranking/{versao}", response_model=List[TbPartidasTstResponse])
async def ranking_jogadores_por_versao(versao: str, db: Session = Depends(get_db)):
    # Subquery para encontrar a menor partida de cada jogador dentro da versão
    subquery = (
        db.query(
            TbPartidasTstModel.steam_id,
            func.min(TbPartidasTstModel.end_time).label("menor_tempo"),
        )
        .filter(TbPartidasTstModel.win == True, TbPartidasTstModel.version == versao)
        .group_by(TbPartidasTstModel.steam_id)
        .subquery()
    )

    alias_partida = aliased(TbPartidasTstModel)

    # Consulta principal: retorna a partida com o menor tempo de cada jogador
    result = (
        db.query(alias_partida)
        .join(
            subquery,
            (alias_partida.steam_id == subquery.c.steam_id)
            & (alias_partida.end_time == subquery.c.menor_tempo),
        )
        .order_by(alias_partida.end_time.asc())
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


# 7.6 Rota GET para consultar em ordem por end_time e win = true com parametros de versão e estágio
@app.get("/ranking/{versao}/{estagio}/", response_model=List[TbPartidasTstResponse])
async def ranking_jogadores_por_versao(
    versao: str, estagio: int, db: Session = Depends(get_db)
):
    # Subquery para encontrar a menor partida de cada jogador dentro da versão
    subquery = (
        db.query(
            TbPartidasTstModel.nome,
            func.min(TbPartidasTstModel.end_time).label("menor_tempo"),
        )
        .filter(
            TbPartidasTstModel.win == True,
            TbPartidasTstModel.version == versao,
            TbPartidasTstModel.stage == estagio,
        )
        .group_by(TbPartidasTstModel.nome)
        .subquery()
    )

    alias_partida = aliased(TbPartidasTstModel)

    # Consulta principal: retorna a partida com o menor tempo de cada jogador
    result = (
        db.query(alias_partida)
        .join(
            subquery,
            (alias_partida.steam_id == subquery.c.steam_id)
            & (alias_partida.end_time == subquery.c.menor_tempo),
        )
        .order_by(alias_partida.end_time.asc())
        .limit(10)
        .all()
    )

    return result


# 8. Rota POST para criar uma nova entrada na tabela
@app.post("/partidas/", response_model=TbPartidasTst)
async def criar_partida(partida: TbPartidasTst, db: Session = Depends(get_db)):
    db_partida = TbPartidasTstModel(
        version=partida.version,
        steam_name=partida.steam_name,
        steam_id=partida.steam_id,
        nome_pc=partida.nome_pc,
        start_time=partida.start_time,
        end_time=partida.end_time,
        multiplayer=partida.multiplayer,
        stage=partida.stage,
        win=partida.win,
        wave=partida.wave,
        enemies_quantity=partida.enemies_quantity,
        total_seconds=partida.total_seconds,
        end_time_text=partida.end_time_text,
        selected_rewards=jsonable_encoder(partida.selected_rewards),
        enemies_damage_data=jsonable_encoder(partida.enemies_damage_data),
        enemy_death_data=jsonable_encoder(partida.enemy_death_data),
        stage_event_data=jsonable_encoder(partida.stage_event_data),
        relics_id=jsonable_encoder(partida.relics_id),
        first_time_relics=partida.first_time_relics,
        final_level=partida.final_level,
        characters_damage_data=jsonable_encoder(partida.characters_damage_data),
        trait_damage_data=jsonable_encoder(partida.trait_damage_data),
        relic_damage_data=jsonable_encoder(partida.relic_damage_data),
        element_damage_data=jsonable_encoder(partida.element_damage_data),
        itens=jsonable_encoder(partida.itens),
        recipes=jsonable_encoder(partida.recipes),
        damage_taken=jsonable_encoder(partida.damage_taken),
        damage_healed=jsonable_encoder(partida.damage_healed),
        coins=partida.coins,
        critical_hit_quantity=partida.critical_hit_quantity,
    )


    db.add(db_partida)
    db.commit()
    db.refresh(db_partida)

    return db_partida
