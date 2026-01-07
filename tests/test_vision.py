from air_hockey.ui.screens.play import PlayScreen


def test_normalize_axis_basic():
    value = PlayScreen._normalize_axis(50, 0, 100, 0, 100)
    assert value == 0.5


def test_normalize_axis_clamps():
    low = PlayScreen._normalize_axis(-10, 0, 100, 0, 100)
    high = PlayScreen._normalize_axis(200, 0, 100, 0, 100)
    assert low == 0.0
    assert high == 1.0


def test_normalize_axis_fallback():
    value = PlayScreen._normalize_axis(100, None, None, 0, 200)
    assert value == 0.5
