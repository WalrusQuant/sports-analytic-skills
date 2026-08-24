"""Feature registry for sports_ds pre-game features."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from sports_ds.features.team_form import DEFAULT_WIN_FEATURE_COLS, RICH_WIN_FEATURE_COLS


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    formula: str
    legality: str
    shift_rule: str
    notes: str = ""


FORM_FEATURE_SPECS: list[FeatureSpec] = [
    FeatureSpec(
        name="is_home",
        formula="1 if focal team is home else 0",
        legality="known at schedule time",
        shift_rule="n/a",
    ),
    FeatureSpec(
        name="pre_win_pct",
        formula="expanding mean of prior won",
        legality="pre-game only",
        shift_rule="groupby(team).shift(1).expanding().mean()",
    ),
    FeatureSpec(
        name="pre_avg_diff",
        formula="expanding mean of prior point_diff",
        legality="pre-game only",
        shift_rule="groupby(team).shift(1).expanding().mean()",
    ),
    FeatureSpec(
        name="pre_games_played",
        formula="count of prior games",
        legality="pre-game only",
        shift_rule="groupby(team).shift(1).expanding().count()",
    ),
    FeatureSpec(
        name="roll3_win_pct",
        formula="rolling mean of prior won (window 3)",
        legality="pre-game only",
        shift_rule="groupby(team).shift(1).rolling(3, min_periods=1).mean()",
    ),
    FeatureSpec(
        name="roll5_diff",
        formula="rolling mean of prior point_diff (window 5)",
        legality="pre-game only",
        shift_rule="groupby(team).shift(1).rolling(5, min_periods=1).mean()",
    ),
    FeatureSpec(
        name="ewma5_win",
        formula="EWMA of prior won (span 5)",
        legality="pre-game only",
        shift_rule="groupby(team).shift(1).ewm(span=5).mean()",
    ),
    FeatureSpec(
        name="ewma5_diff",
        formula="EWMA of prior point_diff (span 5)",
        legality="pre-game only",
        shift_rule="groupby(team).shift(1).ewm(span=5).mean()",
    ),
    FeatureSpec(
        name="rest_days",
        formula="days since previous team game",
        legality="pre-game (schedule known)",
        shift_rule="gameday - prior gameday",
    ),
    FeatureSpec(
        name="feature_win_pct_diff",
        formula="pre_win_pct - opp_pre_win_pct",
        legality="pre-game only (both sides shifted)",
        shift_rule="opponent join on game_id after shift",
    ),
    FeatureSpec(
        name="feature_diff_diff",
        formula="pre_avg_diff - opp_pre_avg_diff",
        legality="pre-game only",
        shift_rule="opponent join on game_id after shift",
    ),
    FeatureSpec(
        name="feature_roll3_win_diff",
        formula="roll3_win_pct - opp_roll3_win_pct",
        legality="pre-game only",
        shift_rule="opponent join on game_id after shift",
    ),
    FeatureSpec(
        name="feature_roll5_diff_diff",
        formula="roll5_diff - opp_roll5_diff",
        legality="pre-game only",
        shift_rule="opponent join on game_id after shift",
    ),
    FeatureSpec(
        name="feature_ewma5_win_diff",
        formula="ewma5_win - opp_ewma5_win",
        legality="pre-game only",
        shift_rule="opponent join after shift",
    ),
    FeatureSpec(
        name="feature_ewma5_diff_diff",
        formula="ewma5_diff - opp_ewma5_diff",
        legality="pre-game only",
        shift_rule="opponent join after shift",
    ),
    FeatureSpec(
        name="feature_pf_vs_opp_pa",
        formula="roll5_pf - opp_roll5_pa",
        legality="pre-game only",
        shift_rule="offense form vs opponent defense form",
    ),
    FeatureSpec(
        name="feature_rest_diff",
        formula="rest_days - opp_rest_days",
        legality="pre-game",
        shift_rule="schedule-derived",
    ),
    FeatureSpec(
        name="season_week",
        formula="schedule week number",
        legality="known pre-game",
        shift_rule="n/a",
    ),
    FeatureSpec(
        name="elo_pre",
        formula="as-of Elo before game update",
        legality="pre-game only",
        shift_rule="update ratings only after storing pre values",
        notes="from sports_ds.ratings.elo",
    ),
    FeatureSpec(
        name="elo_diff",
        formula="(elo_pre + home_adv if home else elo_pre) - opp_elo_pre",
        legality="pre-game only",
        shift_rule="as-of before game",
    ),
    FeatureSpec(
        name="pre_fantasy_points_ppr",
        formula="player expanding mean of prior PPR fantasy points",
        legality="pre-game only",
        shift_rule="groupby(player_id).shift(1).expanding().mean()",
        notes="player-level; sports_ds.features.player_form",
    ),
    FeatureSpec(
        name="roll3_fantasy_points_ppr",
        formula="player rolling mean prior PPR (window 3)",
        legality="pre-game only",
        shift_rule="groupby(player_id).shift(1).rolling(3).mean()",
    ),
    FeatureSpec(
        name="ewma5_fantasy_points_ppr",
        formula="player EWMA prior PPR (span 5)",
        legality="pre-game only",
        shift_rule="groupby(player_id).shift(1).ewm(span=5).mean()",
    ),
]


def list_feature_specs() -> list[dict]:
    return [asdict(s) for s in FORM_FEATURE_SPECS]


def print_feature_registry() -> str:
    lines = [
        "# sports_ds feature registry",
        "",
        f"## default win cols ({len(DEFAULT_WIN_FEATURE_COLS)})",
        ", ".join(DEFAULT_WIN_FEATURE_COLS),
        "",
        f"## rich win cols ({len(RICH_WIN_FEATURE_COLS)})",
        ", ".join(RICH_WIN_FEATURE_COLS),
        "",
    ]
    for s in FORM_FEATURE_SPECS:
        lines.append(f"## {s.name}")
        lines.append(f"- formula: {s.formula}")
        lines.append(f"- legality: {s.legality}")
        lines.append(f"- shift_rule: {s.shift_rule}")
        if s.notes:
            lines.append(f"- notes: {s.notes}")
        lines.append("")
    return "\n".join(lines)
