from sqlalchemy.orm import Session
from . import models, schemas

# ---------- Player ----------
def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def get_player_by_name(db: Session, normalized_name: str):
    return db.query(models.Player).filter(models.Player.normalized_name == normalized_name).first()

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()

def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

# ---------- Season ----------
def get_season(db: Session, season_id: int):
    return db.query(models.Season).filter(models.Season.id == season_id).first()

def get_season_by_year(db: Session, year: int):
    return db.query(models.Season).filter(models.Season.year == year).first()

def get_seasons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Season).offset(skip).limit(limit).all()

def create_season(db: Session, season: schemas.SeasonCreate):
    db_season = models.Season(**season.dict())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season

# ---------- PlayerSeason ----------
def get_player_season(db: Session, player_id: int, season_id: int):
    return db.query(models.PlayerSeason).filter(
        models.PlayerSeason.player_id == player_id,
        models.PlayerSeason.season_id == season_id
    ).first()

def get_player_seasons(
    db: Session,
    player_id: int = None,
    season_id: int = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(models.PlayerSeason)
    if player_id:
        query = query.filter(models.PlayerSeason.player_id == player_id)
    if season_id:
        query = query.filter(models.PlayerSeason.season_id == season_id)
    return query.offset(skip).limit(limit).all()

def create_player_season(db: Session, player_season: schemas.PlayerSeasonCreate, player_id: int, season_id: int):
    db_ps = models.PlayerSeason(
        player_id=player_id,
        season_id=season_id,
        **player_season.dict()
    )
    db.add(db_ps)
    db.commit()
    db.refresh(db_ps)
    return db_ps

def update_player_season(db: Session, db_ps: models.PlayerSeason, updates: dict):
    for key, value in updates.items():
        setattr(db_ps, key, value)
    db.commit()
    db.refresh(db_ps)
    return db_ps

def delete_player_season(db: Session, db_ps: models.PlayerSeason):
    db.delete(db_ps)
    db.commit()