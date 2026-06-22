from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from common import crud, schemas, models
from app.dependencies import get_db

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/", response_model=List[schemas.PlayerOut])
def get_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if search:
        # Simple search by normalized_name (case‑insensitive)
        players = db.query(models.Player).filter(
            models.Player.normalized_name.ilike(f"%{search}%")
        ).offset(skip).limit(limit).all()
        return players
    return crud.get_players(db, skip=skip, limit=limit)

@router.get("/{player_id}", response_model=schemas.PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/{player_id}/seasons", response_model=List[schemas.PlayerSeasonOut])
def get_player_seasons(
    player_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    player = crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return crud.get_player_seasons(db, player_id=player_id, skip=skip, limit=limit)

@router.get("/{player_id}/seasons/{season_id}", response_model=schemas.PlayerSeasonOut)
def get_player_season(player_id: int, season_id: int, db: Session = Depends(get_db)):
    ps = crud.get_player_season(db, player_id, season_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Player‑season not found")
    return ps