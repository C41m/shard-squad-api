from typing import List
from pydantic import BaseModel


class TbItens(BaseModel):
    id_item: int
    nome_item: str
