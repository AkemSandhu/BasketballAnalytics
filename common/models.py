from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from .database import Base


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    normalized_name = Column(String, unique=True, index=True)
    display_name = Column(String)


class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, unique=True, index=True)


class PlayerSeason(Base):
    __tablename__ = "player_seasons"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    season_id = Column(Integer, ForeignKey("seasons.id"))

    # ----- Core info (basic identification) -----
    team = Column(String)
    pos = Column(String)
    age = Column(Integer)
    g = Column(Integer)
    gs = Column(Integer)
    mp = Column(Integer)

    # ----- Shooting efficiency (general) -----
    fg_pct = Column(Float)
    fg3_pct = Column(Float)
    fg2_pct = Column(Float)
    efg_pct = Column(Float)
    ts_pct = Column(Float)
    ft_pct = Column(Float)
    ftr = Column(Float)
    three_par = Column(Float)

    # ----- Shooting volume & accuracy by zone -----
    at_rim_fga = Column(Float)
    at_rim_accuracy = Column(Float)
    short_mid_range_fga = Column(Float)
    short_mid_range_accuracy = Column(Float)
    long_mid_range_fga = Column(Float)
    long_mid_range_accuracy = Column(Float)
    corner3_fga = Column(Float)
    corner3_accuracy = Column(Float)
    arc3_fga = Column(Float)
    arc3_accuracy = Column(Float)

    # ----- Advanced box score percentages -----
    orb_pct = Column(Float)
    drb_pct = Column(Float)
    trb_pct = Column(Float)
    ast_pct = Column(Float)
    stl_pct = Column(Float)
    blk_pct = Column(Float)
    tov_pct = Column(Float)
    usg_pct = Column(Float)

    # ----- Advanced impact metrics (the core ones) -----
    per = Column(Float)
    ws_per_48 = Column(Float)
    ows = Column(Float)
    dws = Column(Float)
    bpm = Column(Float)
    obpm = Column(Float)
    dbpm = Column(Float)
    vorp = Column(Float)
    war = Column(Float)
    lebron = Column(Float)
    o_lebron = Column(Float)
    d_lebron = Column(Float)

    # ----- Position estimates -----
    pos_estimate_pg = Column(Float)
    pos_estimate_sg = Column(Float)
    pos_estimate_sf = Column(Float)
    pos_estimate_pf = Column(Float)
    pos_estimate_c = Column(Float)

    # ----- On/Off and plus-minus -----
    on_court_plus_minus = Column(Float)
    on_off_plus_minus = Column(Float)
    on_off_rtg = Column(Float)
    on_def_rtg = Column(Float)

    # ----- Our derived metrics (impact, talent, fit) -----
    impact_score = Column(Float)
    talent_score = Column(Float)
    team_fit = Column(Float)

    # ----- Role assignments -----
    offensive_role = Column(String)
    offensive_fit = Column(Float)
    defensive_role = Column(String)
    defensive_fit = Column(Float)

    # ----- JSON containers -----
    similar_seasons = Column(JSON)
    badges = Column(JSON)

    # ----- Relationships -----
    player = relationship("Player", lazy="joined")
    season = relationship("Season", lazy="joined")

    __table_args__ = (
        Index('ix_player_seasons_player_season', 'player_id', 'season_id', unique=True),
    )