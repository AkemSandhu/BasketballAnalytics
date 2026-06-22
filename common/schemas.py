from pydantic import BaseModel
from typing import List, Dict, Optional

# ---------- Player ----------
class PlayerBase(BaseModel):
    normalized_name: str
    display_name: str

class PlayerCreate(PlayerBase):
    pass

class PlayerOut(PlayerBase):
    id: int

    class Config:
        from_attributes = True

# ---------- Season ----------
class SeasonBase(BaseModel):
    year: int

class SeasonCreate(SeasonBase):
    pass

class SeasonOut(SeasonBase):
    id: int

    class Config:
        from_attributes = True

# ---------- PlayerSeason ----------
class PlayerSeasonBase(BaseModel):
    team: str
    pos: str
    age: Optional[int] = None
    g: Optional[int] = None
    mp: Optional[int] = None
    impact_score: Optional[float] = None
    talent_score: Optional[float] = None
    team_fit: Optional[float] = None
    offensive_role: Optional[str] = None
    offensive_fit: Optional[float] = None
    defensive_role: Optional[str] = None
    defensive_fit: Optional[float] = None
    similar_seasons: Optional[List[Dict]] = None
    badges: Optional[Dict[str, str]] = None

class PlayerSeasonCreate(PlayerSeasonBase):
    pass

class PlayerSeasonOut(PlayerSeasonBase):
    id: int
    player_id: int
    season_id: int

    class Config:
        from_attributes = True