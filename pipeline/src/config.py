from pathlib import Path
from dataclasses import dataclass
import os

PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_OUTPUT = PROJECT_ROOT / "data" / "outputs"

DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
DATA_OUTPUT.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Paths:
    lebron: Path = DATA_RAW / "lebron_data.csv"
    sportsref_dir: Path = DATA_RAW / "sportsref"
    pbpstats_dir: Path = DATA_RAW / "pbpstats"
    name_db: Path = DATA_PROCESSED / "name_mapping.sqlite"
    final_output: Path = DATA_OUTPUT / "nba_complete_analytics.csv"   # kept for fallback


@dataclass(frozen=True)
class BadgeThresholds:
    bronze: float = 75.0
    silver: float = 91.6667
    gold: float = 97.2222
    diamond: float = 99.0741


@dataclass(frozen=True)
class ModelParams:
    impact_n_trials: int = 30
    impact_n_estimators: int = 300
    impact_max_depth: int = 5
    impact_learning_rate: float = 0.03
    talent_n_estimators: int = 200
    talent_max_depth: int = 4


# Database settings (can be overridden by environment variables)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nbadb")

PATHS = Paths()
BADGE_THRESHOLDS = BadgeThresholds()
MODEL_PARAMS = ModelParams()