from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from common import crud, schemas, models
from app.dependencies import get_db

router = APIRouter(prefix="/seasons", tags=["seasons"])

# ------------------------------------------------------------------
# SPECIFIC ROUTES (must be before any route with path parameter)
# ------------------------------------------------------------------

@router.get("/all-player-seasons")
def get_all_player_seasons(
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all player-seasons across all seasons (no season filter)."""
    query = db.query(models.PlayerSeason).join(models.Season).join(models.Player)
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    result = []
    for ps in items:
        player = crud.get_player(db, ps.player_id)
        season = crud.get_season(db, ps.season_id)
        result.append({
            "player_name": player.display_name if player else "Unknown",
            "season": season.year if season else None,
            "team": ps.team,
            "pos": ps.pos,
            "age": ps.age,
            "mp": ps.mp,
            "offensive_role": ps.offensive_role,
            "offensive_fit": ps.offensive_fit,
            "defensive_role": ps.defensive_role,
            "defensive_fit": ps.defensive_fit,
            "impact_score": ps.impact_score,
            "o_lebron": ps.o_lebron,
            "d_lebron": ps.d_lebron,
            "war": ps.war,
            "vorp": ps.vorp,
            "ws_per_48": ps.ws_per_48,
            "talent_score": ps.talent_score,
            "obpm": ps.obpm,
            "dbpm": ps.dbpm,
            "team_fit": ps.team_fit,
            "usg_pct": ps.usg_pct,
            "ts_pct": ps.ts_pct,
            "per": ps.per,
        })
    return {"total": total, "items": result}


@router.get("/{season_id}/player-seasons")
def get_player_seasons_by_season(
    season_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all player-seasons for a specific season."""
    season = crud.get_season(db, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    query = db.query(models.PlayerSeason).filter(models.PlayerSeason.season_id == season_id)
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    result = []
    for ps in items:
        player = crud.get_player(db, ps.player_id)
        result.append({
            "id": ps.id,
            "player_id": ps.player_id,
            "player_name": player.display_name if player else "Unknown",
            "season": season.year,
            "team": ps.team,
            "pos": ps.pos,
            "age": ps.age,
            "mp": ps.mp,
            "offensive_role": ps.offensive_role,
            "offensive_fit": ps.offensive_fit,
            "defensive_role": ps.defensive_role,
            "defensive_fit": ps.defensive_fit,
            "impact_score": ps.impact_score,
            "o_lebron": ps.o_lebron,
            "d_lebron": ps.d_lebron,
            "war": ps.war,
            "vorp": ps.vorp,
            "ws_per_48": ps.ws_per_48,
            "talent_score": ps.talent_score,
            "obpm": ps.obpm,
            "dbpm": ps.dbpm,
            "team_fit": ps.team_fit,
            "usg_pct": ps.usg_pct,
            "ts_pct": ps.ts_pct,
            "per": ps.per,
        })
    return {"total": total, "items": result}


@router.get("/{season_id}/leaders")
def get_leaderboard(
    season_id: int,
    stat: str = Query("impact_score", pattern="^(impact_score|talent_score|team_fit|pts|ast|trb|stl|blk)$"),
    n: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    season = crud.get_season(db, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    from sqlalchemy import desc
    results = db.query(models.PlayerSeason).filter(
        models.PlayerSeason.season_id == season_id
    ).order_by(desc(getattr(models.PlayerSeason, stat))).limit(n).all()
    leaderboard = []
    for ps in results:
        player = crud.get_player(db, ps.player_id)
        leaderboard.append({
            "player_id": ps.player_id,
            "player_name": player.display_name if player else "Unknown",
            "season": season.year,
            stat: getattr(ps, stat)
        })
    return leaderboard


# ------------------------------------------------------------------
# PARAMETERIZED ROUTES (must be after specific routes)
# ------------------------------------------------------------------

@router.get("/", response_model=List[schemas.SeasonOut])
def get_seasons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_seasons(db, skip=skip, limit=limit)


@router.get("/{season_id}", response_model=schemas.SeasonOut)
def get_season(season_id: int, db: Session = Depends(get_db)):
    season = crud.get_season(db, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return season

print("Available routes in seasons router:")
for route in router.routes:
    print(route.path)