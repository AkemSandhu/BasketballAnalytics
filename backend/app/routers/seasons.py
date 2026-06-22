from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from common import models
from common.database import SessionLocal

router = APIRouter(prefix="/seasons", tags=["seasons"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
            "player_name": ps.player.display_name if ps.player else "Unknown",
            "season": ps.season.year if ps.season else None,
            "team": ps.team,
            "pos": ps.pos,
            "age": ps.age,
            "g": ps.g,
            "gs": ps.gs,
            "mp": ps.mp,
            "fg_pct": ps.fg_pct,
            "fg3_pct": ps.fg3_pct,
            "fg2_pct": ps.fg2_pct,
            "efg_pct": ps.efg_pct,
            "ts_pct": ps.ts_pct,
            "ft_pct": ps.ft_pct,
            "ftr": ps.ftr,
            "three_par": ps.three_par,
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
            "orb_pct": ps.orb_pct,
            "drb_pct": ps.drb_pct,
            "trb_pct": ps.trb_pct,
            "ast_pct": ps.ast_pct,
            "stl_pct": ps.stl_pct,
            "blk_pct": ps.blk_pct,
            "tov_pct": ps.tov_pct,
            "usg_pct": ps.usg_pct,
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
            "pos_estimate_pg": ps.pos_estimate_pg,
            "pos_estimate_sg": ps.pos_estimate_sg,
            "pos_estimate_sf": ps.pos_estimate_sf,
            "pos_estimate_pf": ps.pos_estimate_pf,
            "pos_estimate_c": ps.pos_estimate_c,
            "on_court_plus_minus": ps.on_court_plus_minus,
            "on_off_plus_minus": ps.on_off_plus_minus,
            "on_off_rtg": ps.on_off_rtg,
            "on_def_rtg": ps.on_def_rtg,
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