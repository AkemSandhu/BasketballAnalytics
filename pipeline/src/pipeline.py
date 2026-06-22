import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data_loader import merge_all
from src.features import build_feature_set
from src.clustering import add_roles
from src.impact_model import build_composite_target, remove_team_bias, train_impact_model, predict_impact
from src.badge_assigner import compute_skill_badges
from src.similarity import compute_similar_seasons
from src.talent_model import train_talent_model, compute_talent_and_fit
from common.database import Base, engine, SessionLocal
from common.models import Player, Season, PlayerSeason
from sqlalchemy.dialects.postgresql import insert as pg_insert

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
    Base.metadata.create_all(bind=engine)

    # Use display name as primary player name
    if 'Player_display' in df.columns:
        df['Player'] = df['Player_display']
    else:
        df['Player'] = df['Player']

    # ---- Bulk insert players ----
    player_names = df['Player'].unique()
    player_records = [{'normalized_name': name, 'display_name': name} for name in player_names]
    with SessionLocal() as session:
        if player_records:
            stmt = pg_insert(Player).values(player_records)
            stmt = stmt.on_conflict_do_nothing(index_elements=['normalized_name'])
            session.execute(stmt)
        session.commit()

    # ---- Bulk insert seasons ----
    season_years = df['season'].unique()
    season_records = [{'year': int(y)} for y in season_years]
    with SessionLocal() as session:
        if season_records:
            stmt = pg_insert(Season).values(season_records)
            stmt = stmt.on_conflict_do_nothing(index_elements=['year'])
            session.execute(stmt)
        session.commit()

    # ---- Load ID mappings ----
    with SessionLocal() as session:
        players_in_db = {p.normalized_name: p.id for p in session.query(Player).all()}
        seasons_in_db = {s.year: s.id for s in session.query(Season).all()}

    # ---- Build PlayerSeason upsert records ----
    badge_cols = [c for c in df.columns if '_badge' in c]
    ps_records = []
    for _, row in df.iterrows():
        player_name = row['Player']
        season_year = int(row['season'])

        player_id = players_in_db[player_name]
        season_id = seasons_in_db[season_year]

        # Badges JSON
        badges_dict = {}
        for col in badge_cols:
            if pd.notna(row[col]):
                badges_dict[col.replace('_badge', '')] = row[col]
        badges_serializable = convert_to_serializable(badges_dict)

        # Similar seasons
        similar_raw = row.get('similar_seasons', [])
        similar_serializable = convert_to_serializable(similar_raw)

        ps_record = {
            'player_id': player_id,
            'season_id': season_id,
            'team': row.get('Team'),
            'pos': row.get('Pos'),
            'age': row.get('Age'),
            'g': row.get('G'),
            'gs': row.get('GS'),
            'mp': row.get('MP'),
            'fg_pct': row.get('FG%'),
            'fg3_pct': row.get('3P%'),
            'fg2_pct': row.get('2P%'),
            'efg_pct': row.get('eFG%'),
            'ts_pct': row.get('TS%'),
            'ft_pct': row.get('FT%'),
            'ftr': row.get('FTr'),
            'three_par': row.get('3PAr'),
            'at_rim_fga': row.get('AtRimFGA'),
            'at_rim_accuracy': row.get('AtRimAccuracy'),
            'short_mid_range_fga': row.get('ShortMidRangeFGA'),
            'short_mid_range_accuracy': row.get('ShortMidRangeAccuracy'),
            'long_mid_range_fga': row.get('LongMidRangeFGA'),
            'long_mid_range_accuracy': row.get('LongMidRangeAccuracy'),
            'corner3_fga': row.get('Corner3FGA'),
            'corner3_accuracy': row.get('Corner3Accuracy'),
            'arc3_fga': row.get('Arc3FGA'),
            'arc3_accuracy': row.get('Arc3Accuracy'),
            'orb_pct': row.get('ORB%'),
            'drb_pct': row.get('DRB%'),
            'trb_pct': row.get('TRB%'),
            'ast_pct': row.get('AST%'),
            'stl_pct': row.get('STL%'),
            'blk_pct': row.get('BLK%'),
            'tov_pct': row.get('TOV%'),
            'usg_pct': row.get('USG%'),
            'per': row.get('PER'),
            'ws_per_48': row.get('WS/48'),
            'ows': row.get('OWS'),
            'dws': row.get('DWS'),
            'bpm': row.get('BPM'),
            'obpm': row.get('OBPM'),
            'dbpm': row.get('DBPM'),
            'vorp': row.get('VORP'),
            'war': row.get('WAR'),
            'lebron': row.get('LEBRON'),
            'o_lebron': row.get('O-LEBRON'),
            'd_lebron': row.get('D-LEBRON'),
            'pos_estimate_pg': row.get('Position Estimate_PG%'),
            'pos_estimate_sg': row.get('Position Estimate_SG%'),
            'pos_estimate_sf': row.get('Position Estimate_SF%'),
            'pos_estimate_pf': row.get('Position Estimate_PF%'),
            'pos_estimate_c': row.get('Position Estimate_C%'),
            'on_court_plus_minus': row.get('+/- Per 100 Poss_OnCourt'),
            'on_off_plus_minus': row.get('+/- Per 100 Poss_On-Off'),
            'on_off_rtg': row.get('OnOffRtg'),
            'on_def_rtg': row.get('OnDefRtg'),
            'impact_score': row.get('impact_score'),
            'talent_score': row.get('talent_score'),
            'team_fit': row.get('team_fit'),
            'offensive_role': row.get('offensive_role'),
            'offensive_fit': row.get('offensive_fit'),
            'defensive_role': row.get('defensive_role'),
            'defensive_fit': row.get('defensive_fit'),
            'similar_seasons': similar_serializable,
            'badges': badges_serializable,
        }
        ps_records.append(ps_record)

    # ---- Bulk upsert PlayerSeason records ----
    with SessionLocal() as session:
        if ps_records:
            stmt = pg_insert(PlayerSeason).values(ps_records)
            # Update all columns on conflict (except the primary key id)
            update_cols = {c.name: stmt.excluded[c.name] for c in PlayerSeason.__table__.columns if c.name != 'id'}
            stmt = stmt.on_conflict_do_update(
                index_elements=['player_id', 'season_id'],
                set_=update_cols
            )
            session.execute(stmt)
        session.commit()

    print("Database write complete (bulk).")

if __name__ == "__main__":
    run_pipeline()