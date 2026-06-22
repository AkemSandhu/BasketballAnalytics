import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, mutual_info_regression
from sklearn.linear_model import BayesianRidge, ElasticNetCV
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold
import xgboost as xgb
from src.config import MODEL_PARAMS

def build_composite_target(df):
    sources = []
    if "LEBRON" in df.columns:
        sources.append(("LEBRON", df["LEBRON"]))
    if "BPM" in df.columns:
        sources.append(("BPM", df["BPM"]))
    if "+/- Per 100 Poss_On-Off" in df.columns:
        sources.append(("OnOff", df["+/- Per 100 Poss_On-Off"]))
    if not sources:
        raise ValueError("No target columns found")
    composite = np.zeros(len(df))
    for name, vals in sources:
        z = vals.copy()
        for season in df["season"].unique():
            mask = df["season"] == season
            season_vals = vals[mask]
            mean = season_vals.mean()
            std = season_vals.std()
            if std > 0:
                z.loc[mask] = (vals.loc[mask] - mean) / std
            else:
                z.loc[mask] = vals.loc[mask] - mean
        composite += z
    composite /= len(sources)
    return composite

def remove_team_bias(df, target_col):
    """
    Subtract the team‑average of target_col (per season) from each player,
    excluding the player themselves (leave‑one‑out). Vectorised using groupby.
    """
    # Team average = (sum(team) - self) / (count - 1)
    team_sum = df.groupby(['Team', 'season'])[target_col].transform('sum')
    team_count = df.groupby(['Team', 'season'])[target_col].transform('count')
    adjusted = df[target_col] - (team_sum - df[target_col]) / (team_count - 1)
    return adjusted.values

def select_features(X, y, k=40):
    selector = SelectKBest(mutual_info_regression, k=min(k, X.shape[1]))
    X_sel = selector.fit_transform(X, y)
    return X_sel, selector.get_support()

def train_impact_model(df, feature_cols, target_col):
    model_df = df.dropna(subset=[target_col] + feature_cols).copy()
    X_raw = model_df[feature_cols].values
    y = model_df[target_col].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    X_sel, mask = select_features(X_scaled, y)
    selected_features = [feature_cols[i] for i in range(len(feature_cols)) if mask[i]]
    print(f"Selected {len(selected_features)} features.")

    xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=-1)
    ridge = BayesianRidge(max_iter=300, tol=1e-3, alpha_1=1e-6, lambda_1=1e-6)
    elastic = ElasticNetCV(l1_ratio=[.1, .5, .7, .9, .95, .99, 1], cv=5, random_state=42)
    rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)

    param_grid = {
        'n_estimators': [200, 300],
        'max_depth': [3, 4, 5],
        'learning_rate': [0.01, 0.03, 0.05],
        'subsample': [0.7, 0.8],
        'colsample_bytree': [0.7, 0.8],
        'reg_alpha': [0.1, 1.0],
        'reg_lambda': [0.5, 1.0]
    }
    grid = GridSearchCV(xgb_model, param_grid, cv=5, scoring='r2', verbose=0, n_jobs=-1)
    grid.fit(X_sel, y)
    best_xgb = grid.best_estimator_
    print(f"XGBoost CV R²: {grid.best_score_:.3f}")

    stack = StackingRegressor(
        estimators=[
            ('xgb', best_xgb),
            ('ridge', ridge),
            ('elastic', elastic),
            ('rf', rf)
        ],
        final_estimator=BayesianRidge(max_iter=300),
        cv=5
    )
    stack.fit(X_sel, y)

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(stack, X_sel, y, cv=cv, scoring='r2')
    print(f"Ensemble cross‑validated R²: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

    return stack, scaler, mask, feature_cols

def predict_impact(df, model, scaler, mask, feature_cols):
    X_all = df[feature_cols].values
    X_scaled = scaler.transform(X_all)
    X_sel = X_scaled[:, mask]
    impact = model.predict(X_sel)
    impact = impact - impact.mean()
    return impact