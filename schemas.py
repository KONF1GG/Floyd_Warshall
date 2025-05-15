from typing import List, Literal, Optional
from pydantic import BaseModel
from pydantic import field_validator

class Locality(BaseModel):
    city1: str
    city2: str
    min: float
    km: Optional[float] = None
    
    @field_validator('min', 'km')
    def check_positive(cls, v):
        if v < 0:
            raise ValueError('Distance cannot be negative')
        return v

class LocalityResponse(BaseModel):
    data: List[Locality] = []
    error: Optional[str] = None

class Ural(BaseModel):
    ural: Literal[1, 2]