from pydantic import BaseModel
from typing import Optional

class Link(BaseModel):
    href: str
    rel: str
    type: str
    title: str

class Geometry(BaseModel):
    type: str
    coordinates: list[float]