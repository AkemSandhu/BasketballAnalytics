import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import umap
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

# ------------------------ Offensive feature collection ------------------------
def _get_offensive_features(df):
    features = []
    # Per‑36 tendencies (already computed in features.py)
    if "AST_per36" in df.columns:
        features.append("AST_per36")
    if "ORB_per36" in df.columns:
        features.append("ORB_per36")
    for col in ["AtRimFGA_per36", "ShortMidRangeFGA_per36", "LongMidRangeFGA_per36",
                "Corner3FGA_per36", "Arc3FGA_per36"]:
        if col in df.columns:
            features.append(col)
    # Position estimates
    pos_cols = [c for c in df.columns if "Position Estimate_" in c]
    features.extend(pos_cols)
    # OffRole one‑hot (from lebron)
    if "OffRole" in df.columns:
        off_dummies = pd.get_dummies(df["OffRole"], prefix="OffRole")
        df = pd.concat([df, off_dummies], axis=1)
        features.extend(off_dummies.columns)
    return [f for f in features if f in df.columns], df

# ------------------------ Defensive feature collection ------------------------
def _get_defensive_features(df):
    features = []
    for col in ["BLK_per36", "STL_per36", "DRB_per36"]:
        if col in df.columns:
            features.append(col)
    pos_cols = [c for c in df.columns if "Position Estimate_" in c]
    features.extend(pos_cols)
    if "DefRole" in df.columns:
        def_dummies = pd.get_dummies(df["DefRole"], prefix="DefRole")
        df = pd.concat([df, def_dummies], axis=1)
        features.extend(def_dummies.columns)
    return [f for f in features if f in df.columns], df

# ------------------------ Clustering and naming (identical to original) ------------------------
def _cluster_and_name(df, feature_cols, n_clusters=8, random_state=42):
    X = df[feature_cols].copy()
    # Drop columns that are entirely NaN
    X = X.dropna(axis=1, how='all')
    if X.shape[1] == 0:
        return ["Role Player"] * len(df), np.zeros(len(df))
    # Fill remaining NaNs with column median
    X = X.fillna(X.median())
    # Replace infinities
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    if X.shape[0] < n_clusters:
        return ["Role Player"] * len(df), np.zeros(len(df))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # UMAP to 2D for stability (same as original)
    reducer = umap.UMAP(n_components=2, random_state=random_state)
    X_umap = reducer.fit_transform(X_scaled)
    # KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_umap)
    # Fit score = 1 - distance to centroid (scaled 0-1)
    distances = pairwise_distances(X_umap, kmeans.cluster_centers_)
    min_dist = distances.min(axis=1)
    max_possible = np.max(min_dist) + 1e-6
    fit = 1 - (min_dist / max_possible)
    # Name clusters based on top positive deviations (original logic)
    global_mean = X_scaled.mean(axis=0)
    role_names = {}
    for i in range(n_clusters):
        centroid = X_scaled[labels == i].mean(axis=0)
        dev = centroid - global_mean
        top_idx = np.argsort(dev)[-2:]  # two strongest features
        top_feats = [feature_cols[idx] for idx in top_idx]
        name_parts = []
        for f in top_feats:
            fl = f.lower()
            if "atrim" in fl:
                name_parts.append("Slasher")
            elif "arc3" in fl:
                name_parts.append("Shooter")
            elif "ast" in fl:
                name_parts.append("Playmaker")
            elif "blk" in fl:
                name_parts.append("Rim Protector")
            elif "stl" in fl:
                name_parts.append("Ball Hawk")
            elif "orb" in fl:
                name_parts.append("Off.Reb.")
            elif "drb" in fl:
                name_parts.append("Def.Reb.")
            elif "position_estimate_c" in fl:
                name_parts.append("Big")
            elif "position_estimate_pg" in fl:
                name_parts.append("PG")
            elif "offrole_" in fl:
                name_parts.append(fl.split("_")[-1])
            elif "defrole_" in fl:
                name_parts.append(fl.split("_")[-1])
        if not name_parts:
            name_parts = ["Role Player"]
        role_names[i] = " / ".join(name_parts[:2])
    role_labels = [role_names[l] for l in labels]
    return role_labels, fit

# ------------------------ Main function: add roles to dataframe ------------------------
def add_roles(df):
    # Ensure we have a copy to avoid fragmentation warnings
    df = df.copy()
    off_features, df = _get_offensive_features(df)
    if off_features:
        off_labels, off_fit = _cluster_and_name(df, off_features, n_clusters=8)
        df["offensive_role"] = off_labels
        df["offensive_fit"] = off_fit
    else:
        df["offensive_role"] = "Role Player"
        df["offensive_fit"] = 0.0

    def_features, df = _get_defensive_features(df)
    if def_features:
        def_labels, def_fit = _cluster_and_name(df, def_features, n_clusters=6)
        df["defensive_role"] = def_labels
        df["defensive_fit"] = def_fit
    else:
        df["defensive_role"] = "Standard Defender"
        df["defensive_fit"] = 0.0

    return df