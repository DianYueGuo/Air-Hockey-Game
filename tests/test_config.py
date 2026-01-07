from air_hockey.config import io
from air_hockey.config.settings import Settings
from air_hockey.engine.calibration import CalibrationData, PlayerCalibration


def test_settings_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "get_user_data_dir", lambda: tmp_path)
    settings = Settings(theme="retro", fullscreen=True, display_index=2)
    io.save_settings(settings)
    loaded = io.load_settings()
    assert loaded.theme == settings.theme
    assert loaded.fullscreen == settings.fullscreen
    assert loaded.display_index == settings.display_index


def test_calibration_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "get_user_data_dir", lambda: tmp_path)
    calibration = CalibrationData(
        left=PlayerCalibration(cam_x_min=10, cam_x_max=200, cam_y_min=5, cam_y_max=180),
        right=PlayerCalibration(cam_x_min=12, cam_x_max=220, cam_y_min=8, cam_y_max=190),
    )
    io.save_calibration(calibration)
    loaded = io.load_calibration()
    assert loaded.left.cam_x_min == 10
    assert loaded.left.cam_x_max == 200
    assert loaded.right.cam_y_min == 8
    assert loaded.right.cam_y_max == 190
