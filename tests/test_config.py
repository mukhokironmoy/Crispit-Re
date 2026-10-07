from pathlib import Path

import pytest
from pydantic import ValidationError

from crispit.core.config import Settings

SETTING_VARIABLES = (
    "CRISPIT_APP_NAME",
    "CRISPIT_APP_ENVIRONMENT",
    "CRISPIT_LOG_LEVEL",
)


def clear_settings_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove Crispit settings from the test environment."""

    for variable in SETTING_VARIABLES:
        monkeypatch.delenv(variable, raising=False)


def test_settings_have_safe_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:

    # Check to see that if no system variables are given does the settings class handle it with default values
    clear_settings_environment(monkeypatch)
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_name == "Crispit"
    assert settings.app_environment == "development"
    assert settings.log_level == "INFO"


def test_settings_read_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:

    # If a valid value is given as system variables, does the settings class handle it properly
    clear_settings_environment(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CRISPIT_APP_ENVIRONMENT", "test")
    monkeypatch.setenv("CRISPIT_LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.app_environment == "test"
    assert settings.log_level == "DEBUG"


def test_settings_reject_invalid_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:

    # If an invalid value is given as system variables, does the settings class throw an error
    clear_settings_environment(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CRISPIT_APP_ENVIRONMENT", "invalid")

    with pytest.raises(ValidationError):
        Settings()