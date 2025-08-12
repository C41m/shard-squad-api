from typing import List
from pydantic import BaseModel


class TbPersonagens(BaseModel):
    id_personagem: int
    nome_personagem: str
