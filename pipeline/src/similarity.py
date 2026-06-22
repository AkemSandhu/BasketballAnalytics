import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from src.clustering import _get_offensive_features, _get_defensive_features

def compute_similar_seasons(df, n_neighbors=5):
    """
    Compute similar seasons based purely on playstyle tendencies and role fits.
    Uses the same offensive and defensive features as clustering, plus offensive_fit and defensive_fit.
    Season penalty: exp(-|season_diff|/3).
    """
    # Get tendency features from clustering functions
    off_features, _ = _get_offensive_features(df.copy())
    def_features, _ = _get_defensive_features(df.copy())
    # Combine unique features
    feature_cols = list(set(off_features + def_features))
    # Add role fit scores (they capture how well the player fits their role)
    if 'offensive_fit' in df.columns:
        feature_cols.append('offensive_fit')
    if 'defensive_fit' in df.columns:
        feature_cols.append('defensive_fit')
    
    if not feature_cols:
        return [[] for _ in range(len(df))]
    
    X = df[feature_cols].copy()
    # Impute missing values with column median, then fill remaining with 0
    X = X.fillna(X.median()).fillna(0)
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Feature weighting: 50% variance, 50% correlation with impact (if available)
    variances = X.var().values
    if 'impact_score' in df.columns:
        corrs = X.corrwith(df['impact_score']).abs().fillna(0).values
        if variances.sum() > 0:
            weight_var = variances / variances.sum()
        else:
            weight_var = np.ones(len(feature_cols)) / len(feature_cols)
        if corrs.sum() > 0:
            weight_corr = corrs / corrs.sum()
        else:
            weight_corr = np.ones(len(feature_cols)) / len(feature_cols)
        feature_weights = (weight_var + weight_corr) / 2
    else:
        if variances.sum() > 0:
            feature_weights = variances / variances.sum()
        else:
            feature_weights = np.ones(len(feature_cols)) / len(feature_cols)
    
    X_weighted = X_scaled * feature_weights
    
    # Cosine similarity via NearestNeighbors (fast)
    nn = NearestNeighbors(n_neighbors=n_neighbors+1, metric='cosine', algorithm='brute', n_jobs=-1)
    nn.fit(X_weighted)
    distances, indices = nn.kneighbors(X_weighted)
    
    # Season penalty: exp(-|season_diff|/3)
    seasons = df['season'].values
    season_diff = np.abs(seasons[:, np.newaxis] - seasons[np.newaxis, :])
    penalty = np.exp(-season_diff / 3)
    
    similar = []
    for i in range(len(df)):
        # Get neighbors excluding self (first neighbor is always self)
        neighbor_indices = indices[i][1:]
        neighbor_dists = distances[i][1:]
        # Convert cosine distance to similarity
        similarities = 1 - neighbor_dists
        # Apply season penalty
        sim_penalized = similarities * penalty[i, neighbor_indices]
        # Sort by penalized similarity (descending)
        order = np.argsort(sim_penalized)[::-1][:n_neighbors]
        top_indices = neighbor_indices[order]
        top_sims = sim_penalized[order]
        top = [(df.iloc[j]["Player_display"], df.iloc[j]["season"], sim)
               for j, sim in zip(top_indices, top_sims)]
        similar.append(top)
    return similar