from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from common import crud, schemas, models
from app.dependencies import get_db

router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("/all")
def get_all_player_seasons(
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all player‑seasons across all seasons.
    Player and Season data are automatically loaded via relationships.
    """
    query = db.query(models.PlayerSeason)
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    result = []
    for ps in items:
        result.append({
            # Core info
            "player_name": ps.player.display_name if ps.player else "Unknown",
            "season": ps.season.year if ps.season else None,
            "team": ps.team,
            "pos": ps.pos,
            "age": ps.age,
            "g": ps.g,
            "gs": ps.gs,
            "mp": ps.mp,

            # Shooting efficiency
            "fg_pct": ps.fg_pct,
            "fg3_pct": ps.fg3_pct,
            "fg2_pct": ps.fg2_pct,
            "efg_pct": ps.efg_pct,
            "ts_pct": ps.ts_pct,
            "ft_pct": ps.ft_pct,
            "ftr": ps.ftr,
            "three_par": ps.three_par,

            # Zone shooting
            "at_rim_fga": ps.at_rim_fga,
            "at_rim_accuracy": ps.at_rim_accuracy,
            "short_mid_range_fga": ps.short_mid_range_fga,
            "short_mid_range_accuracy": ps.short_mid_range_accuracy,
            "long_mid_range_fga": ps.long_mid_range_fga,
            "long_mid_range_accuracy": ps.long_mid_range_accuracy,
            "corner3_fga": ps.corner3_fga,
            "corner3_accuracy": ps.corner3_accuracy,
            "arc3_fga": ps.arc3_fga,
            "arc3_accuracy": ps.arc3_accuracy,

            # Advanced percentages
            "orb_pct": ps.orb_pct,
            "drb_pct": ps.drb_pct,
            "trb_pct": ps.trb_pct,
            "ast_pct": ps.ast_pct,
            "stl_pct": ps.stl_pct,
            "blk_pct": ps.blk_pct,
            "tov_pct": ps.tov_pct,
            "usg_pct": ps.usg_pct,

            # Advanced impact metrics
            "per": ps.per,
            "ws_per_48": ps.ws_per_48,
            "ows": ps.ows,
            "dws": ps.dws,
            "bpm": ps.bpm,
            "obpm": ps.obpm,
            "dbpm": ps.dbpm,
            "vorp": ps.vorp,
            "war": ps.war,
            "lebron": ps.lebron,
            "o_lebron": ps.o_lebron,
            "d_lebron": ps.d_lebron,

            # Position estimates
            "pos_estimate_pg": ps.pos_estimate_pg,
            "pos_estimate_sg": ps.pos_estimate_sg,
            "pos_estimate_sf": ps.pos_estimate_sf,
            "pos_estimate_pf": ps.pos_estimate_pf,
            "pos_estimate_c": ps.pos_estimate_c,

            # On/Off
            "on_court_plus_minus": ps.on_court_plus_minus,
            "on_off_plus_minus": ps.on_off_plus_minus,
            "on_off_rtg": ps.on_off_rtg,
            "on_def_rtg": ps.on_def_rtg,

            # Our derived metrics
            "impact_score": ps.impact_score,
            "talent_score": ps.talent_score,
            "team_fit": ps.team_fit,
            "offensive_role": ps.offensive_role,
            "offensive_fit": ps.offensive_fit,
            "defensive_role": ps.defensive_role,
            "defensive_fit": ps.defensive_fit,
            "badges": ps.badges,
            "similar_seasons": ps.similar_seasons,
        })

    return {"total": total, "items": result}


@router.get("/{season_id}/player-seasons")
def get_player_seasons_by_season(
    season_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all player‑seasons for a specific season."""
    season = crud.get_season(db, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    query = db.query(models.PlayerSeason).filter(models.PlayerSeason.season_id == season_id)
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    result = []
    for ps in items:
        result.append({
            "id": ps.id,
            "player_id": ps.player_id,
            "player_name": ps.player.display_name if ps.player else "Unknown",
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
        leaderboard.append({
            "player_id": ps.player_id,
            "player_name": ps.player.display_name if ps.player else "Unknown",
            "season": season.year,
            stat: getattr(ps, stat)
        })
    return leaderboard


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