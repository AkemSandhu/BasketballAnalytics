import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
from src.config import BADGE_THRESHOLDS

def _normalize_by_role(df, metric, role_col):
    if not isinstance(metric, pd.Series):
        metric = pd.Series(metric, index=df.index)
    result = np.full(len(df), np.nan)
    for role in df[role_col].unique():
        mask = (df[role_col] == role) & metric.notna()
        if mask.sum() == 0:
            continue
        role_vals = metric[mask]
        for idx in df[mask].index:
            val = metric.loc[idx]
            if pd.isna(val):
                continue
            pct = percentileofscore(role_vals, val)
            result[df.index.get_loc(idx)] = pct
    result = np.nan_to_num(result, nan=50.0)
    return result

def _assign_badge(score):
    if pd.isna(score):
        return None
    if score >= BADGE_THRESHOLDS.diamond:
        return "Diamond"
    elif score >= BADGE_THRESHOLDS.gold:
        return "Gold"
    elif score >= BADGE_THRESHOLDS.silver:
        return "Silver"
    elif score >= BADGE_THRESHOLDS.bronze:
        return "Bronze"
    return None

# ------------------------ Shooting Badges ------------------------
def _deadeye(df):
    raw = df["3P%"] * np.log1p(df["3PA"] * 0.5)
    return _normalize_by_role(df, raw, "off_role_group")

def _limitless_range(df):
    if "Arc3Accuracy" in df.columns:
        raw = df["Arc3Accuracy"] * np.log1p(df["Arc3FGA"] * 0.7)
    else:
        raw = df["3P%"] * np.log1p(df["3PA"] * 0.5)
    return _normalize_by_role(df, raw, "off_role_group")

def _set_shot_specialist(df):
    if "Corner3Accuracy" in df.columns:
        raw = df["Corner3Accuracy"] * np.log1p(df["Corner3FGA"] * 0.8)
    else:
        raw = df["3P%"] * np.log1p(df["3PA"] * 0.3)
    return _normalize_by_role(df, raw, "off_role_group")

def _shifty_shooter(df):
    raw = df["3P%"] * (df.get("USG%", 15) / 15)
    score = _normalize_by_role(df, raw, "off_role_group")
    playmaker_weight = df["off_role_group"].apply(lambda x: 1.2 if x == "Playmaker" else 1.0)
    score = score * playmaker_weight
    return _normalize_by_role(df, score, "off_role_group")

def _corner_specialist(df):
    if "Corner3Accuracy" in df.columns:
        raw = df["Corner3Accuracy"] * np.log1p(df["Corner3FGA"])
    else:
        raw = df["3P%"] * np.log1p(df["3PA"] * 0.3)
    return _normalize_by_role(df, raw, "off_role_group")

def _catch_shoot(df):
    raw = df["3P%"] * df.get("Assisted3sPct", 0.7) * np.log1p(df["3PA"] * 0.5)
    return _normalize_by_role(df, raw, "off_role_group")

def _pull_up_assassin(df):
    raw = df["3P%"] * (1 - df.get("Assisted3sPct", 0.3)) * np.log1p(df["3PA"] * 0.5)
    score = _normalize_by_role(df, raw, "off_role_group")
    playmaker_weight = df["off_role_group"].apply(lambda x: 1.2 if x == "Playmaker" else 1.0)
    score = score * playmaker_weight
    return _normalize_by_role(df, score, "off_role_group")

def _mini_marksman(df):
    if all(c in df.columns for c in ["Position Estimate_PG%", "Position Estimate_SG%", "Position Estimate_SF%", "Position Estimate_PF%", "Position Estimate_C%"]):
        height = (df["Position Estimate_PG%"] * 74 +
                  df["Position Estimate_SG%"] * 77 +
                  df["Position Estimate_SF%"] * 79 +
                  df["Position Estimate_PF%"] * 82 +
                  df["Position Estimate_C%"] * 84) / 100
    else:
        height = 79
    raw = df["TS%"] * (74 / (height + 1e-6))
    return _normalize_by_role(df, raw, "off_role_group")

# ------------------------ Finishing Badges ------------------------
def _float_game(df):
    if "ShortMidRangeAccuracy" in df.columns:
        raw = df["ShortMidRangeAccuracy"] * np.log1p(df["ShortMidRangeFGA"] * 0.6)
    else:
        raw = df["2P%"]
    return _normalize_by_role(df, raw, "off_role_group")

def _paint_prodigy(df):
    if "AtRimAccuracy" in df.columns:
        raw = df["AtRimAccuracy"] * np.log1p(df["AtRimFGA"] * 0.7)
    else:
        raw = df["2P%"]
    score = _normalize_by_role(df, raw, "off_role_group")
    slasher_weight = df["off_role_group"].apply(lambda x: 1.3 if x in ["Slasher", "Big", "Stretch Big"] else 1.0)
    score = score * slasher_weight
    return _normalize_by_role(df, score, "off_role_group")

def _physical_finisher(df):
    and1_rate = df.get("Misc._And1", 0) / (df["FGA"] + 1e-6)
    foul_draw_rate = df.get("FoulsDrawn", 0) / (df["FGA"] + 1e-6)
    raw = (and1_rate * 100 + foul_draw_rate * 50) * np.log1p(df.get("AtRimFGA", df["FGA"]))
    return _normalize_by_role(df, raw, "off_role_group")

def _posterizer(df):
    if "AtRimFGA" in df.columns:
        raw = (df["AtRimFGA"] / (df["MP"] + 1e-6) * 36) * df["AtRimAccuracy"]
    else:
        raw = (df["2PA"] / (df["MP"] + 1e-6) * 36) * df["2P%"]
    return _normalize_by_role(df, raw, "off_role_group")

def _contact_finisher(df):
    # Find any column that contains 'FTA' (case insensitive)
    fta_col = None
    for col in df.columns:
        if 'fta' in col.lower():
            fta_col = col
            break
    if fta_col is None:
        return pd.Series([np.nan] * len(df), index=df.index)
    raw = (df[fta_col] / (df["FGA"] + 1e-6)) * df.get("AtRimAccuracy", df["2P%"]) * np.log1p(df.get("AtRimFGA", df["FGA"]))
    # Ensure raw is a Series
    if not isinstance(raw, pd.Series):
        raw = pd.Series(raw, index=df.index)
    return _normalize_by_role(df, raw, "off_role_group")

def _giant_slayer(df):
    if all(c in df.columns for c in ["Position Estimate_PG%", "Position Estimate_SG%", "Position Estimate_SF%", "Position Estimate_PF%", "Position Estimate_C%"]):
        height = (df["Position Estimate_PG%"] * 74 +
                  df["Position Estimate_SG%"] * 77 +
                  df["Position Estimate_SF%"] * 79 +
                  df["Position Estimate_PF%"] * 82 +
                  df["Position Estimate_C%"] * 84) / 100
    else:
        height = 79
    raw = df.get("AtRimAccuracy", df["2P%"]) * (1 / (height + 1e-6)) * np.log1p(df.get("AtRimFGA", df["FGA"]))
    score = _normalize_by_role(df, raw, "off_role_group")
    short_bonus = (height < 76).astype(float) * 0.3
    score = score * (1 + short_bonus)
    return _normalize_by_role(df, score, "off_role_group")

def _rise_up(df):
    raw = df.get("AtRimFGA", df["2PA"]) / (df["MP"] + 1e-6) * 36
    return _normalize_by_role(df, raw, "off_role_group")

def _aerial_wizard(df):
    raw = df.get("AtRimAccuracy", df["2P%"]) * df.get("ORB%", 0) * np.log1p(df.get("AtRimFGA", df["FGA"]))
    return _normalize_by_role(df, raw, "off_role_group")

def _post_fade_phenom(df):
    if "LongMidRangeAccuracy" in df.columns:
        raw = df["LongMidRangeAccuracy"] * (df.get("Position Estimate_C%", 0) / 100 + 0.5)
    else:
        raw = df["2P%"] * (df.get("Position Estimate_C%", 0) / 100 + 0.5)
    return _normalize_by_role(df, raw, "off_role_group")

# ------------------------ Playmaking Badges ------------------------
def _dimer(df):
    raw = df["AST%"] * (df.get("AssistPoints", df["AST"]) / (df["AST"] + 1e-6))
    score = _normalize_by_role(df, raw, "off_role_group")
    playmaker_weight = df["off_role_group"].apply(lambda x: 1.2 if x == "Playmaker" else 1.0)
    score = score * playmaker_weight
    return _normalize_by_role(df, score, "off_role_group")

def _ankle_assassin(df):
    raw = df.get("USG%", 15) * (1 - df.get("Assisted2sPct", 0.5))
    score = _normalize_by_role(df, raw, "off_role_group")
    score = score * (df["off_role_group"] == "Playmaker").astype(float) * 0.2 + score
    return _normalize_by_role(df, score, "off_role_group")

def _unpluckable(df):
    if "TOV%" in df.columns:
        raw = df.get("USG%", 15) / (df["TOV%"] + 1e-6)
    else:
        raw = df["AST"] / (df["TOV"] + 1e-6)
    return _normalize_by_role(df, raw, "off_role_group")

def _break_starter(df):
    raw = df.get("DRB%", 0) * df.get("AST%", 0) / 100
    return _normalize_by_role(df, raw, "off_role_group")

def _versatile_visionary(df):
    if "AssistPoints" in df.columns:
        raw = df["AssistPoints"] / (df["MP"] + 1e-6) * 36
    else:
        raw = df["AST"] / (df["MP"] + 1e-6) * 36
    score = _normalize_by_role(df, raw, "off_role_group")
    playmaker_weight = df["off_role_group"].apply(lambda x: 1.2 if x == "Playmaker" else 1.0)
    score = score * playmaker_weight
    return _normalize_by_role(df, score, "off_role_group")

def _handles_for_days(df):
    raw = df.get("USG%", 15) * (100 - df.get("TOV%", 0)) / 100
    return _normalize_by_role(df, raw, "off_role_group")

# ------------------------ Defensive Badges ------------------------
def _pickpocket(df):
    raw = df["STL%"] if "STL%" in df.columns else df["STL"] / (df["MP"] + 1e-6) * 36
    return _normalize_by_role(df, raw, "def_role_group")

def _interceptor(df):
    if "BadPassSteals" in df.columns:
        raw = df["BadPassSteals"] / (df["MP"] + 1e-6) * 36
    else:
        raw = _pickpocket(df)
    return _normalize_by_role(df, raw, "def_role_group")

def _rim_protector(df):
    raw = df["BLK%"] if "BLK%" in df.columns else df["BLK"] / (df["MP"] + 1e-6) * 36
    score = _normalize_by_role(df, raw, "def_role_group")
    big_weight = df["def_role_group"].apply(lambda x: 1.3 if x == "Big" else 1.0)
    score = score * big_weight
    return _normalize_by_role(df, score, "def_role_group")

def _paint_patroller(df):
    raw = _rim_protector(df) * (df.get("Position Estimate_C%", 0) / 100 + 0.5)
    return _normalize_by_role(df, raw, "def_role_group")

def _on_ball_menace(df):
    raw = df.get("D-LEBRON", 0) + df.get("STL%", 0) / 10
    score = _normalize_by_role(df, raw, "def_role_group")
    perimeter_weight = df["def_role_group"].apply(lambda x: 1.3 if x == "Perimeter" else 1.0)
    score = score * perimeter_weight
    return _normalize_by_role(df, score, "def_role_group")

def _challenger(df):
    raw = df.get("DBPM", 0) + df.get("D-LEBRON", 0) / 2
    return _normalize_by_role(df, raw, "def_role_group")

def _post_lockdown(df):
    raw = df.get("D-LEBRON", 0) * (df.get("Position Estimate_C%", 0) / 100)
    return _normalize_by_role(df, raw, "def_role_group")

# ------------------------ Rebounding Badges ------------------------
def _off_rebound_hunter(df):
    raw = df["ORB%"] if "ORB%" in df.columns else df["ORB"] / (df["MP"] + 1e-6) * 36
    return _normalize_by_role(df, raw, "def_role_group")

def _def_rebound_vacuum(df):
    raw = df["DRB%"] if "DRB%" in df.columns else df["DRB"] / (df["MP"] + 1e-6) * 36
    return _normalize_by_role(df, raw, "def_role_group")

def _box_out_guru(df):
    raw = _def_rebound_vacuum(df) * (df.get("Position Estimate_C%", 0) / 100 + 0.5)
    return _normalize_by_role(df, raw, "def_role_group")

def _putback_boss(df):
    raw = _off_rebound_hunter(df) * df.get("AtRimAccuracy", df["2P%"])
    return _normalize_by_role(df, raw, "def_role_group")

# ------------------------ Special Badges ------------------------
def _microwave(df):
    if "GS" in df.columns and "impact_score" in df.columns:
        is_bench = (df["GS"] / (df["G"] + 1e-6)) < 0.5
        raw = df["impact_score"] * is_bench.astype(int) + df["PTS"] / (df["MP"] + 1e-6) * 36 * 0.5
    else:
        raw = df["PTS"] / (df["MP"] + 1e-6) * 36
    return _normalize_by_role(df, raw, "off_role_group")

def _closer(df):
    raw = df.get("impact_score", df.get("LEBRON", 0)) + 5 + df.get("USG%", 15) / 10
    return _normalize_by_role(df, raw, "off_role_group")

def _transition_phenom(df):
    raw = df.get("AtRimAccuracy", df["2P%"]) * (df["PTS"] / (df["MP"] + 1e-6) * 36)
    score = _normalize_by_role(df, raw, "off_role_group")
    transition_weight = df["off_role_group"].apply(lambda x: 1.2 if x in ["Slasher", "Athletic Finisher"] else 1.0)
    score = score * transition_weight
    return _normalize_by_role(df, score, "off_role_group")

def _one_man_wrecking_crew(df):
    raw = (1 - df.get("Assisted2sPct", 0.5)) * df.get("USG%", 15)
    return _normalize_by_role(df, raw, "off_role_group")

def _consistency(df):
    raw = df["G"] * df.get("PER", 15) / 15
    return raw

def _streaky(df):
    cons = _consistency(df)
    raw = 100 - cons
    return _normalize_by_role(df, raw, "off_role_group")

def _nuclear_upside(df):
    raw = df.get("impact_score", df.get("LEBRON", 0)) * df.get("USG%", 15)
    return _normalize_by_role(df, raw, "off_role_group")

# ------------------------ Main aggregator ------------------------
def compute_skill_badges(df, off_role_col="offensive_role", def_role_col="defensive_role"):
    def get_primary_role(role_str):
        if not isinstance(role_str, str):
            return "Wing"
        primary = role_str.split(" / ")[0].strip()
        lower = primary.lower()
        if "play" in lower:
            return "Playmaker"
        if "slash" in lower or "finish" in lower:
            return "Slasher"
        if "shoot" in lower:
            return "Shooter"
        if "rim" in lower or "protect" in lower:
            return "Big"
        if "off.reb" in lower or "def.reb" in lower:
            return "Big"
        return "Wing"

    off_groups = {
        "Playmaker": "Playmaker",
        "Slasher": "Slasher",
        "Shooter": "Shooter",
        "Big": "Big",
        "Stretch Big": "Stretch Big",
        "Wing": "Wing"
    }
    def_groups = {
        "Point of Attack": "Perimeter",
        "Chaser": "Perimeter",
        "Helper": "Wing",
        "Low Activity": "Wing",
        "Wing Stopper": "Perimeter",
        "Mobile Big": "Big",
        "Anchor Big": "Big",
        "Standard Defender": "Wing",
        "Rim Protector": "Big",
        "Ball Hawk": "Perimeter"
    }

    df["off_role_group"] = df[off_role_col].apply(get_primary_role).map(off_groups).fillna("Wing")
    df["def_role_group"] = df[def_role_col].apply(get_primary_role).map(def_groups).fillna("Wing")

    badge_functions = {
        "Deadeye": _deadeye,
        "Limitless Range": _limitless_range,
        "Set Shot Specialist": _set_shot_specialist,
        "Shifty Shooter": _shifty_shooter,
        "Corner Specialist": _corner_specialist,
        "Catch & Shoot": _catch_shoot,
        "Pull-Up Assassin": _pull_up_assassin,
        "Mini Marksman": _mini_marksman,
        "Float Game": _float_game,
        "Paint Prodigy": _paint_prodigy,
        "Physical Finisher": _physical_finisher,
        "Posterizer": _posterizer,
        "Contact Finisher": _contact_finisher,
        "Giant Slayer": _giant_slayer,
        "Rise Up": _rise_up,
        "Aerial Wizard": _aerial_wizard,
        "Post Fade Phenom": _post_fade_phenom,
        "Dimer": _dimer,
        "Ankle Assassin": _ankle_assassin,
        "Unpluckable": _unpluckable,
        "Break Starter": _break_starter,
        "Versatile Visionary": _versatile_visionary,
        "Handles for Days": _handles_for_days,
        "Pickpocket": _pickpocket,
        "Interceptor": _interceptor,
        "Rim Protector": _rim_protector,
        "Paint Patroller": _paint_patroller,
        "On‑Ball Menace": _on_ball_menace,
        "Challenger": _challenger,
        "Post Lockdown": _post_lockdown,
        "Offensive Rebound Hunter": _off_rebound_hunter,
        "Defensive Rebound Vacuum": _def_rebound_vacuum,
        "Box Out Guru": _box_out_guru,
        "Putback Boss": _putback_boss,
        "Microwave": _microwave,
        "Closer": _closer,
        "Transition Phenom": _transition_phenom,
        "One‑Man Wrecking Crew": _one_man_wrecking_crew,
        "Consistency": _consistency,
        "Streaky": _streaky,
        "Nuclear Upside": _nuclear_upside,
    }

    score_df = pd.DataFrame(index=df.index)
    badge_df = pd.DataFrame(index=df.index)

    for name, func in badge_functions.items():
        try:
            scores = func(df)
            if not isinstance(scores, pd.Series):
                scores = pd.Series(scores, index=df.index)
            badge_df[f"{name}_badge"] = [_assign_badge(s) for s in scores]
            score_df[f"{name}_score"] = scores
        except Exception as e:
            print(f"Warning: could not compute badge {name}: {e}")
            badge_df[f"{name}_badge"] = None
            score_df[f"{name}_score"] = np.nan

    return score_df, badge_df