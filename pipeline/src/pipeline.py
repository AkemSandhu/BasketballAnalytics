import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import PATHS, DATABASE_URL
from src.data_loader import merge_all
from src.features import build_feature_set
from src.clustering import add_roles
from src.impact_model import build_composite_target, remove_team_bias, train_impact_model, predict_impact
from src.badge_assigner import compute_skill_badges
from src.similarity import compute_similar_seasons
from src.talent_model import train_talent_model, compute_talent_and_fit
from common.database import Base, engine, SessionLocal
from common.models import Player, Season, PlayerSeason

warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

def convert_to_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(i) for i in obj]
    return obj

def run_pipeline():
    print("Loading and merging data (original method)...")
    df = merge_all()
    print(f"Merged shape: {df.shape}")

    print("3. Feature engineering (per36, interactions)...")
    df = build_feature_set(df)

    print("4. Role clustering (offensive & defensive)...")
    df = add_roles(df)

    print("5. Building impact score (original stacking ensemble)...")
    composite = build_composite_target(df)
    df["composite_target"] = composite
    df["target"] = remove_team_bias(df, "composite_target")
    print(f"Rows with non‑null target: {df['target'].notna().sum()}")

    exclude = ["Player", "season", "Team", "Pos", "composite_target", "target",
               "offensive_role", "defensive_role", "Player_display"]
    impact_features = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
    print(f"Number of impact features: {len(impact_features)}")

    model, scaler, mask, feat_list = train_impact_model(df, impact_features, "target")
    df["impact_score"] = predict_impact(df, model, scaler, mask, feat_list)
    print(f"Impact score range: {df['impact_score'].min():.2f} to {df['impact_score'].max():.2f}")

    print("6. Computing skill badges...")
    df["offensive_role"] = df["offensive_role"].astype(str)
    df["defensive_role"] = df["defensive_role"].astype(str)
    badge_scores_df, badge_tiers_df = compute_skill_badges(df, off_role_col="offensive_role", def_role_col="defensive_role")
    df = pd.concat([df, badge_scores_df, badge_tiers_df], axis=1)

    print("7. Finding similar seasons...")
    df["similar_seasons"] = compute_similar_seasons(df, n_neighbors=5)

    print("8. Talent and team fit...")
    talent_features = [c for c in impact_features if c not in ["team_quality"]]
    talent_model, talent_scaler = train_talent_model(df, talent_features, target_col="impact_score")
    talent, team_fit = compute_talent_and_fit(df, talent_model, talent_scaler, talent_features)
    df["talent_score"] = talent
    df["team_fit"] = team_fit

    print("9. Writing to PostgreSQL database...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Drop and recreate all tables to ensure the schema matches the current models
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database schema recreated.")

    # Use display name as primary player name
    if 'Player_display' in df.columns:
        df['Player'] = df['Player_display']
    else:
        df['Player'] = df['Player']

    for _, row in df.iterrows():
        # Player
        player = session.query(Player).filter_by(normalized_name=row['Player']).first()
        if not player:
            player = Player(normalized_name=row['Player'], display_name=row['Player'])
            session.add(player)
            session.flush()

        # Season
        season = session.query(Season).filter_by(year=int(row['season'])).first()
        if not season:
            season = Season(year=int(row['season']))
            session.add(season)
            session.flush()

        # Build badges JSON
        badge_cols = [c for c in df.columns if '_badge' in c]
        badges_dict = {col.replace('_badge', ''): row[col] for col in badge_cols if pd.notna(row[col])}
        badges_serializable = convert_to_serializable(badges_dict)

        # Similar seasons conversion
        similar_raw = row.get('similar_seasons', [])
        similar_serializable = convert_to_serializable(similar_raw)

        # PlayerSeason (upsert)
        ps = session.query(PlayerSeason).filter_by(
            player_id=player.id,
            season_id=season.id
        ).first()
        if ps is None:
            ps = PlayerSeason(player_id=player.id, season_id=season.id)
            session.add(ps)

        # Core info
        ps.team = row.get('Team')
        ps.pos = row.get('Pos')
        ps.age = row.get('Age')
        ps.g = row.get('G')
        ps.gs = row.get('GS')
        ps.mp = row.get('MP')

        # Shooting efficiency
        ps.fg_pct = row.get('FG%')
        ps.fg3_pct = row.get('3P%')
        ps.fg2_pct = row.get('2P%')
        ps.efg_pct = row.get('eFG%')
        ps.ts_pct = row.get('TS%')
        ps.ft_pct = row.get('FT%')
        ps.ftr = row.get('FTr')
        ps.three_par = row.get('3PAr')

        # Zone shooting (volume & accuracy)
        ps.at_rim_fga = row.get('AtRimFGA')
        ps.at_rim_accuracy = row.get('AtRimAccuracy')
        ps.short_mid_range_fga = row.get('ShortMidRangeFGA')
        ps.short_mid_range_accuracy = row.get('ShortMidRangeAccuracy')
        ps.long_mid_range_fga = row.get('LongMidRangeFGA')
        ps.long_mid_range_accuracy = row.get('LongMidRangeAccuracy')
        ps.corner3_fga = row.get('Corner3FGA')
        ps.corner3_accuracy = row.get('Corner3Accuracy')
        ps.arc3_fga = row.get('Arc3FGA')
        ps.arc3_accuracy = row.get('Arc3Accuracy')

        # Advanced percentages
        ps.orb_pct = row.get('ORB%')
        ps.drb_pct = row.get('DRB%')
        ps.trb_pct = row.get('TRB%')
        ps.ast_pct = row.get('AST%')
        ps.stl_pct = row.get('STL%')
        ps.blk_pct = row.get('BLK%')
        ps.tov_pct = row.get('TOV%')
        ps.usg_pct = row.get('USG%')

        # Advanced impact metrics
        ps.per = row.get('PER')
        ps.ws_per_48 = row.get('WS/48')
        ps.ows = row.get('OWS')
        ps.dws = row.get('DWS')
        ps.bpm = row.get('BPM')
        ps.obpm = row.get('OBPM')
        ps.dbpm = row.get('DBPM')
        ps.vorp = row.get('VORP')
        ps.war = row.get('WAR')
        ps.lebron = row.get('LEBRON')
        ps.o_lebron = row.get('O-LEBRON')
        ps.d_lebron = row.get('D-LEBRON')

        # Position estimates
        ps.pos_estimate_pg = row.get('Position Estimate_PG%')
        ps.pos_estimate_sg = row.get('Position Estimate_SG%')
        ps.pos_estimate_sf = row.get('Position Estimate_SF%')
        ps.pos_estimate_pf = row.get('Position Estimate_PF%')
        ps.pos_estimate_c = row.get('Position Estimate_C%')

        # On/Off
        ps.on_court_plus_minus = row.get('+/- Per 100 Poss_OnCourt')
        ps.on_off_plus_minus = row.get('+/- Per 100 Poss_On-Off')
        ps.on_off_rtg = row.get('OnOffRtg')
        ps.on_def_rtg = row.get('OnDefRtg')

        # Our derived metrics
        ps.impact_score = row.get('impact_score')
        ps.talent_score = row.get('talent_score')
        ps.team_fit = row.get('team_fit')
        ps.offensive_role = row.get('offensive_role')
        ps.offensive_fit = row.get('offensive_fit')
        ps.defensive_role = row.get('defensive_role')
        ps.defensive_fit = row.get('defensive_fit')
        ps.similar_seasons = similar_serializable
        ps.badges = badges_serializable

    session.commit()
    session.close()
    print("Database write complete.")

if __name__ == "__main__":
    run_pipeline()