from sports_ds.features.registry import DEFAULT_WIN_FEATURE_COLS, list_feature_specs, print_feature_registry


def test_feature_registry_nonempty():
    specs = list_feature_specs()
    assert len(specs) >= 8
    names = {s["name"] for s in specs}
    assert "feature_win_pct_diff" in names
    assert "elo_diff" in names
    assert "is_home" in DEFAULT_WIN_FEATURE_COLS
    text = print_feature_registry()
    assert "feature_win_pct_diff" in text
