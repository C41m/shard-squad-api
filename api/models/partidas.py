from sqlalchemy import Column, Integer, String, Boolean, Float, Numeric
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TbPartidasTstModel(Base):
    __tablename__ = "tb_partidas_tst2"

    # General Info
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String)  # version
    steam_name = Column(String)  # steamName
    steam_id = Column(Numeric(100, 0))  # steamID (ulong)
    nome_pc = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    multiplayer = Column(Boolean)

    # Stage Info
    stage = Column(Integer)
    win = Column(Boolean)
    wave = Column(Integer)
    enemies_quantity = Column(Integer)
    total_seconds = Column(Float)
    end_time_text = Column(String)
    selected_rewards = Column(JSON)
    enemies_damage_data = Column(JSON)
    enemy_death_data = Column(JSON)
    stage_event_data = Column(JSON)

    # Relic Info
    relics_id = Column(JSON)
    first_time_relics = Column(Integer)

    # Character Info
    final_level = Column(Integer)
    characters_damage_data = Column(JSON)
    trait_damage_data = Column(JSON)
    relic_damage_data = Column(JSON)
    element_damage_data = Column(JSON)
    itens = Column(JSON)
    recipes = Column(JSON)
    damage_taken = Column(JSON)  # lista de floats
    damage_healed = Column(JSON)  # lista de floats
    coins = Column(Integer)
    critical_hit_quantity = Column(Integer)



