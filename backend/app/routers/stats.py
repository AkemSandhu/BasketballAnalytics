from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from common import crud, models
from app.dependencies import get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/player/{player_id}/radar/{season_id}")
def get_radar_data(player_id: int, season_id: int, db: Session = Depends(get_db)):
    """Return badge tiers as a dict for radar chart."""
    ps = crud.get_player_season(db, player_id, season_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Player‑season not found")
    if not ps.badges:
        return {}
    # badges is JSON dict: {"Deadeye": "Gold", "Rim Protector": "Silver", ...}
    return ps.badges


@router.get("/player/{player_id}/timeline")
def get_player_timeline(player_id: int, db: Session = Depends(get_db)):
    """Return impact_score, talent_score, team_fit over all seasons for a player."""
    seasons_data = crud.get_player_seasons(db, player_id=player_id)
    if not seasons_data:
        raise HTTPException(status_code=404, detail="No data for this player")

    timeline = []
    for ps in seasons_data:
        season = crud.get_season(db, ps.season_id)
        timeline.append({
            "season": season.year if season else ps.season_id,
            "impact_score": ps.impact_score,
            "talent_score": ps.talent_score,
            "team_fit": ps.team_fit
        })
    # sort by season year
    timeline.sort(key=lambda x: x["season"])
    return timeline


@router.get("/similar/{player_id}/{season_id}")
def get_similar_seasons(player_id: int, season_id: int, db: Session = Depends(get_db)):
    """Return pre‑computed similar seasons from JSONB column."""
    ps = crud.get_player_season(db, player_id, season_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Player‑season not found")
    return ps.similar_seasons or []