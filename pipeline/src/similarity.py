import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

def compute_similar_seasons(df, n_neighbors=5):
    """
    Compute similar seasons based on playstyle tendencies and role fits.
    Uses features already present in the DataFrame (from clustering step).
    """
    # Offensive tendency features (per‑36 shot profiles + position estimates)
    off_features = []
    for col in ['AST_per36', 'ORB_per36',
                'AtRimFGA_per36', 'ShortMidRangeFGA_per36', 'LongMidRangeFGA_per36',
                'Corner3FGA_per36', 'Arc3FGA_per36']:
        if col in df.columns:
            off_features.append(col)
    # Position estimates
    pos_cols = [c for c in df.columns if c.startswith('Position Estimate_')]
    off_features.extend(pos_cols)

    # Defensive tendency features
    def_features = []
    for col in ['BLK_per36', 'STL_per36', 'DRB_per36']:
        if col in df.columns:
            def_features.append(col)
    def_features.extend(pos_cols)  # position again

    # Combine unique features
    feature_cols = list(set(off_features + def_features))

    # Add role fit scores
    if 'offensive_fit' in df.columns:
        feature_cols.append('offensive_fit')
    if 'defensive_fit' in df.columns:
        feature_cols.append('defensive_fit')

    if not feature_cols:
        return [[] for _ in range(len(df))]

    X = df[feature_cols].copy()
    X = X.fillna(X.median()).fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Feature weighting: 50% variance, 50% correlation with impact (if available)
    variances = X.var().values
    if 'impact_score' in df.columns:
        corrs = X.corrwith(df['impact_score']).abs().fillna(0).values
    else:
        corrs = np.zeros(len(feature_cols))

    if variances.sum() > 0:
        weight_var = variances / variances.sum()
    else:
        weight_var = np.ones(len(feature_cols)) / len(feature_cols)

    if corrs.sum() > 0:
        weight_corr = corrs / corrs.sum()
    else:
        weight_corr = np.ones(len(feature_cols)) / len(feature_cols)

    feature_weights = (weight_var + weight_corr) / 2
    X_weighted = X_scaled * feature_weights

    nn = NearestNeighbors(n_neighbors=n_neighbors + 1, metric='cosine', algorithm='brute', n_jobs=-1)
    nn.fit(X_weighted)
    distances, indices = nn.kneighbors(X_weighted)

    # Season penalty
    seasons = df['season'].values
    season_diff = np.abs(seasons[:, np.newaxis] - seasons[np.newaxis, :])
    penalty = np.exp(-season_diff / 3)

    similar = []
    for i in range(len(df)):
        neighbor_indices = indices[i][1:]
        neighbor_dists = distances[i][1:]
        similarities = 1 - neighbor_dists
        sim_penalized = similarities * penalty[i, neighbor_indices]
        order = np.argsort(sim_penalized)[::-1][:n_neighbors]
        top_indices = neighbor_indices[order]
        top_sims = sim_penalized[order]
        top = [(df.iloc[j]["Player_display"], df.iloc[j]["season"], sim)
               for j, sim in zip(top_indices, top_sims)]
        similar.append(top)
    return similar