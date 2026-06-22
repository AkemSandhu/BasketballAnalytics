import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from src.config import MODEL_PARAMS

def train_talent_model(df, skill_features, target_col="impact_score"):
    X = df[skill_features].fillna(df[skill_features].median())
    y = df[target_col].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = xgb.XGBRegressor(
        n_estimators=MODEL_PARAMS.talent_n_estimators,
        max_depth=MODEL_PARAMS.talent_max_depth,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled, y)
    return model, scaler

def compute_talent_and_fit(df, model, scaler, skill_features, target_col="impact_score"):
    X = df[skill_features].fillna(df[skill_features].median())
    X_scaled = scaler.transform(X)
    base_talent = model.predict(X_scaled)

    player_best_off = df.groupby('Player')['offensive_fit'].max().to_dict()
    player_best_def = df.groupby('Player')['defensive_fit'].max().to_dict()

    talent = np.zeros(len(df))
    impact = df[target_col].values
    for pos, (_, row) in enumerate(df.iterrows()):
        player = row['Player']
        curr_off = row.get('offensive_fit', 0.5)
        curr_def = row.get('defensive_fit', 0.5)
        best_off = player_best_off.get(player, curr_off)
        best_def = player_best_def.get(player, curr_def)
        off_ratio = best_off / (curr_off + 1e-6)
        def_ratio = best_def / (curr_def + 1e-6)
        multiplier = min(off_ratio * def_ratio, 1.5)
        talent[pos] = base_talent[pos] * multiplier
        talent[pos] = max(talent[pos], impact[pos])

    # Original team fit calculation: shift both impact and talent by the same offset
    min_val = min(impact.min(), talent.min()) - 0.5
    team_fit = (impact - min_val) / (talent - min_val)
    team_fit = np.clip(team_fit, 0, 1)
    return talent, team_fit