from pydantic import BaseModel
from datetime import datetime
from .dmi import Link, Geometry
from uuid import UUID
from typing import Optional

class StationProperty(BaseModel):
    owner: str
    country: str
    anemometerHeight: Optional[float]
    barometerHeight: Optional[float]
    stationHeight: Optional[float]
    wmoCountryCode: Optional[str]
    wmoStationId: Optional[str]
    stationId: str
    regionId: Optional[str]
    name: str
    type: str
    status: str
    parameterId: str | list[str]
    operationFrom: datetime
    operationTo: Optional[datetime]
    validFrom: datetime
    validTo: Optional[datetime]
    created: datetime
    updated: Optional[datetime]

class StationFeature(BaseModel):
    type: str
    id: UUID
    geometry: Geometry
    properties: StationProperty

class StationFeatureCollection(BaseModel):
    type: str
    features: list[StationFeature]
    timeStamp: str
    numberReturned: int
    links: list[Link]