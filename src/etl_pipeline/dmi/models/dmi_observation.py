from pydantic import BaseModel
from datetime import datetime
from .dmi import Link, Geometry
from uuid import UUID
from typing import Optional

class ObservationProperty(BaseModel):
    parameterId: str
    created: datetime
    value: float
    observed: datetime
    stationId: str

class ObservationFeature(BaseModel):
    type: str
    id: UUID
    geometry: Geometry
    properties: ObservationProperty

class ObservationFeatureCollection(BaseModel):
    type: str
    features: list[ObservationFeature]
    timeStamp: str
    numberReturned: int
    links: list[Link]