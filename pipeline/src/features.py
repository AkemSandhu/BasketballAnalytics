import pandas as pd
import numpy as np

def add_per36(df):
    if "MP" not in df.columns:
        return df
    mp36 = df["MP"] / 36.0
    mp36 = mp36.replace(0, np.nan)
    new_cols = {}
    for col in ["PTS", "AST", "TRB", "STL", "BLK", "ORB", "DRB", "FGA", "3PA", "FTA"]:
        if col in df.columns:
            new_cols[f"{col}_per36"] = df[col] / mp36
    shot_cols = ["AtRimFGA", "ShortMidRangeFGA", "LongMidRangeFGA", "Corner3FGA", "Arc3FGA"]
    for col in shot_cols:
        if col in df.columns:
            new_cols[f"{col}_per36"] = df[col] / mp36
    if new_cols:
        df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)
    return df

def add_interactions(df):
    new_cols = {}
    if "USG%" in df and "TS%" in df:
        new_cols["USG_TS"] = df["USG%"] * df["TS%"]
    if "AST%" in df and "USG%" in df:
        new_cols["AST_USG"] = df["AST%"] * df["USG%"]
    if "BLK%" in df and "D-LEBRON" in df:
        new_cols["BLK_DLEBRON"] = df["BLK%"] * df["D-LEBRON"]
    if "3PAr" in df and "3P%" in df:
        new_cols["3PAr_3Pct"] = df["3PAr"] * df["3P%"]
    if "STL%" in df and "DBPM" in df:
        new_cols["STL_DBPM"] = df["STL%"] * df["DBPM"]
    if "TRB%" in df and "AST%" in df:
        new_cols["TRB_AST"] = df["TRB%"] * df["AST%"]
    if new_cols:
        df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)
    return df

def build_feature_set(df):
    df = add_per36(df)
    df = add_interactions(df)
    return df