"""Config persistence helpers."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from air_hockey.config.settings import Settings
from air_hockey.engine.calibration import CalibrationData, PlayerCalibration

APP_NAME = "AirHockey"


def get_user_data_dir() -> Path:
    home = Path.home()
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return base / APP_NAME
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    return home / ".local" / "share" / APP_NAME.lower()


def _calibration_path() -> Path:
    return get_user_data_dir() / "calibration.json"


def _settings_path() -> Path:
    return get_user_data_dir() / "settings.json"


def load_calibration() -> CalibrationData:
    path = _calibration_path()
    if not path.exists():
        return CalibrationData(left=PlayerCalibration(), right=PlayerCalibration())
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return CalibrationData(left=PlayerCalibration(), right=PlayerCalibration())
    return CalibrationData.from_dict(data.get("calibration", {}))


def save_calibration(calibration: CalibrationData) -> None:
    path = _calibration_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"calibration": calibration.to_dict()}
    path.write_text(json.dumps(payload, indent=2))


def load_settings() -> Settings:
    path = _settings_path()
    if not path.exists():
        return Settings()
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return Settings()
    return Settings.from_dict(data.get("settings", {}))


def save_settings(settings: Settings) -> None:
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"settings": settings.to_dict()}
    path.write_text(json.dumps(payload, indent=2))
