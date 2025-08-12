from typing import List
from pydantic import BaseModel


class EnemyDamageDataJson(BaseModel):
    id: str
    damage: float


class EnemyDeathDataJson(BaseModel):
    id: str
    quantity: int


class StageEventDataJson(BaseModel):
    id: str
    completed: bool


class ItemJson(BaseModel):
    id: int
    level: int


class RecipeJson(BaseModel):
    id: int
    level: int


class ElementDamageDataJson(BaseModel):
    element: int
    damage: float


class CharacterDamageDataJson(BaseModel):
    start_second: float
    character: int
    damage: float
    damage_boss: float
    dps: float
    upgrade_indexes: List[int]


class TbPartidasTst(BaseModel):
    # General Info
    version: str
    steam_name: str
    steam_id: int
    nome_pc: str
    start_time: str
    end_time: str
    multiplayer: bool

    # Stage Info
    stage: int
    win: bool
    wave: int
    enemies_quantity: int
    total_seconds: float
    end_time_text: str
    selected_rewards: List[str]
    enemies_damage_data: List[EnemyDamageDataJson]
    enemy_death_data: List[EnemyDeathDataJson]
    stage_event_data: List[StageEventDataJson]

    # Relic Info
    relics_id: List[str]
    first_time_relics: int

    # Character Info
    final_level: int
    characters_damage_data: List[CharacterDamageDataJson]
    trait_damage_data: CharacterDamageDataJson
    relic_damage_data: CharacterDamageDataJson
    element_damage_data: List[ElementDamageDataJson]
    itens: List[ItemJson]
    recipes: List[RecipeJson]
    damage_taken: List[float]
    damage_healed: List[float]
    coins: int
    critical_hit_quantity: int
