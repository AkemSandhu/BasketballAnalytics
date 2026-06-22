import pandas as pd
import re
import unicodedata
import glob
from pathlib import Path
from rapidfuzz import fuzz, process
from tqdm import tqdm
from src.config import PATHS

# ------------------------ Helper functions (identical to original) ------------------------
def normalize_name(name):
    if not isinstance(name, str):
        return ""
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = name.lower()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'\b(jr|sr|iii|iv|ii)\b', '', name).strip()
    return name

def load_or_create_mapping(canonical_names, other_names, existing_mapping, fuzzy_threshold=70):
    norm_canonical = {name: normalize_name(name) for name in canonical_names}
    norm_other = {name: normalize_name(name) for name in other_names}
    mapping = {}
    unmatched = []
    for other_name, norm_other_name in norm_other.items():
        if other_name in existing_mapping:
            mapping[other_name] = existing_mapping[other_name]
            continue
        matches = process.extract(
            norm_other_name,
            list(norm_canonical.values()),
            scorer=fuzz.ratio,
            limit=1
        )
        if matches and matches[0][1] >= fuzzy_threshold:
            best_match_norm = matches[0][0]
            best_canonical = [cn for cn, ncn in norm_canonical.items() if ncn == best_match_norm][0]
            mapping[other_name] = best_canonical
        else:
            unmatched.append(other_name)
            mapping[other_name] = other_name
    return mapping, unmatched

# ------------------------ SportsRef: merge totals, advanced, pbp per season -----------------
def load_sportsref():
    # Dictionary to hold dataframes per season
    season_data = {}
    subfolders = ["totals", "advanced", "pbp"]
    for sub in subfolders:
        sub_dir = PATHS.sportsref_dir / sub
        if not sub_dir.exists():
            continue
        files = glob.glob(str(sub_dir / "sportsref_*.xls*"))
        for fpath in tqdm(files, desc=f"Loading sportsref/{sub}"):
            year = int(re.search(r"(\d{4})", fpath).group(1))
            tables = pd.read_html(fpath)
            if not tables:
                continue
            df = tables[0]
            # flatten multiindex
            if isinstance(df.columns, pd.MultiIndex):
                new_cols = []
                for tup in df.columns:
                    parts = [str(p).strip() for p in tup if p and 'Unnamed' not in str(p)]
                    if not parts:
                        parts = ['col']
                    new_cols.append('_'.join(parts))
                df.columns = new_cols
            if "Player" not in df.columns:
                first = df.columns[0]
                df = df.rename(columns={first: "Player"})
            df["season"] = year
            # drop unwanted columns (identical to original)
            drop_cols = ["Rk", "Awards"]
            if sub != "totals":
                drop_cols += ["Age", "Team", "Pos", "G", "GS", "MP"]
            df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore", inplace=True)
            df["Player"] = df["Player"].astype(str).str.strip()
            # Store per season and subfolder
            season_data.setdefault(year, {})[sub] = df

    # Merge per season: totals + advanced + pbp (outer join)
    merged_by_season = {}
    for year, sub_dfs in season_data.items():
        if not all(s in sub_dfs for s in subfolders):
            missing = [s for s in subfolders if s not in sub_dfs]
            print(f"Skipping {year} – missing: {missing}")
            continue
        merged = sub_dfs["totals"]
        merged = pd.merge(merged, sub_dfs["advanced"], on=["Player", "season"], how="outer")
        merged = pd.merge(merged, sub_dfs["pbp"], on=["Player", "season"], how="outer")
        merged_by_season[year] = merged

    if not merged_by_season:
        raise ValueError("No sportsref data merged")
    combined = pd.concat(merged_by_season.values(), ignore_index=True)
    # Drop Team and Pos as original (they come from lebron)
    combined.drop(columns=["Team", "Pos"], inplace=True, errors="ignore")
    return combined

# ------------------------ PBPstats: merge all subfolders per season ------------------------
def load_pbpstats():
    subfolders = ["assists", "distribution", "fouls", "fts", "misc", "nof", "rebounds", "scoring", "turnovers"]
    drop_cols = ["TeamAbbreviation", "GamesPlayed", "Minutes"]
    season_dfs = {}
    for sub in subfolders:
        sub_dir = PATHS.pbpstats_dir / sub
        if not sub_dir.is_dir():
            continue
        files = glob.glob(str(sub_dir / "pbpstats_export_*.csv"))
        for fpath in tqdm(files, desc=f"Loading pbpstats/{sub}"):
            year = int(re.search(r"(\d{4})", fpath).group(1))
            df = pd.read_csv(fpath)
            if "Name" in df.columns:
                df = df.rename(columns={"Name": "Player"})
            if sub != "scoring":
                df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore", inplace=True)
            df["season"] = year
            df["Player"] = df["Player"].astype(str).str.strip()
            season_dfs.setdefault(year, []).append(df)

    merged_by_season = {}
    for year, dfs in season_dfs.items():
        merged = dfs[0]
        for df in dfs[1:]:
            merged = pd.merge(merged, df, on=["Player", "season"], how="outer")
        merged_by_season[year] = merged

    if not merged_by_season:
        raise ValueError("No pbpstats data merged")
    combined = pd.concat(merged_by_season.values(), ignore_index=True)
    return combined

# ------------------------ LEBRON loader (unchanged) ---------------------------------------
def load_lebron():
    df = pd.read_csv(PATHS.lebron)
    df = df.rename(columns={"Season": "season"})
    df["season"] = df["season"].astype(int)
    if "MPG" in df.columns:
        df.drop(columns=["MPG"], inplace=True)
    return df

# ------------------------ Name mapping helpers --------------------------------------------
def load_manual_mapping():
    mapping_file = PATHS.name_db.parent / "name_mapping.csv"
    if mapping_file.exists():
        df = pd.read_csv(mapping_file)
        return dict(zip(df["original_name"], df["canonical_name"]))
    return {}

def save_unmatched(unmatched, filename):
    if unmatched:
        log_file = PATHS.name_db.parent / filename
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("UNMATCHED NAMES\n")
            f.write("\n".join(unmatched))
        print(f"Unmatched names saved to {log_file}")

# ------------------------ Main merge function (exactly as original) -----------------------
def merge_all():
    # Load raw data (already merged per season)
    lebron_df = load_lebron()
    sportsref_df = load_sportsref()
    pbp_df = load_pbpstats()

    # Build name mappings
    canonical_names = sportsref_df["Player"].dropna().unique()
    other_names_lebron = lebron_df["Player"].dropna().unique()
    other_names_pbp = pbp_df["Player"].dropna().unique()
    manual_mapping = load_manual_mapping()
    lebron_mapping, lebron_unmatched = load_or_create_mapping(canonical_names, other_names_lebron, manual_mapping)
    pbp_mapping, pbp_unmatched = load_or_create_mapping(canonical_names, other_names_pbp, manual_mapping)
    save_unmatched(lebron_unmatched, "unmatched_lebron.txt")
    save_unmatched(pbp_unmatched, "unmatched_pbp.txt")

    # Apply mappings
    lebron_df["Player"] = lebron_df["Player"].map(lebron_mapping)
    pbp_df["Player"] = pbp_df["Player"].map(pbp_mapping)
    lebron_df.dropna(subset=["Player"], inplace=True)
    pbp_df.dropna(subset=["Player"], inplace=True)

    # Merge (outer joins)
    merged = pd.merge(lebron_df, sportsref_df, on=["Player", "season"], how="outer")
    merged = pd.merge(merged, pbp_df, on=["Player", "season"], how="outer")

    # Drop rows missing critical columns (Player, season, PTS, LEBRON)
    critical = ["Player", "season", "PTS", "LEBRON"]
    before = len(merged)
    merged.dropna(subset=critical, inplace=True)
    print(f"Dropped {before - len(merged)} rows missing {critical}")
    merged.drop_duplicates(subset=["Player", "season"], keep="first", inplace=True)

    # Keep a display name (original lebron name if available)
    if 'Player_x' in merged.columns:
        merged['Player_display'] = merged['Player_x'].fillna(merged['Player'])
        merged.drop(columns=['Player_x'], inplace=True)
    else:
        merged['Player_display'] = merged['Player']

    # Remove any remaining _y columns if the original column already exists
    for col in list(merged.columns):
        if col.endswith('_y') and col[:-2] in merged.columns:
            merged.drop(columns=[col], inplace=True)
    # Drop rows with any missing value (clean up incomplete records)
    before = len(merged)
    merged = merged.dropna()
    print(f"Dropped {before - len(merged)} rows with any missing stats")
    print(f"Merged shape: {merged.shape}")
    return merged