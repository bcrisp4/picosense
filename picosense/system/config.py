import json

from typing import Any, Dict


class ConfigError(Exception):
    """Custom exception for configuration errors."""

    pass


class Config:
    """Class to handle loading and accessing configuration data."""

    def __init__(self, path: str = "config.json") -> None:
        """
        Initialize the Config object.

        Args:
            path (str): Path to the configuration file.
        """
        self._path = path

        try:
            with open(path, "r") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Configuration file {path} not found!")
        except ValueError:
            raise ConfigError(f"Configuration file {path} is not valid JSON!")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")

    @property
    def path(self) -> str:
        """Return the path to the configuration file."""
        return self._path

    @property
    def data(self) -> Dict[str, Any]:
        """Return the configuration data."""
        return self._data

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access to the configuration data."""
        try:
            return self._data[key]
        except KeyError as e:
            raise ConfigError(f"Key {key} not found in configuration!") from e

    def __repr__(self) -> str:
        """Return a string representation of the configuration data."""
        return json.dumps(self._data)

    def __str__(self) -> str:
        """Return a string representation of the configuration data."""
        return json.dumps(self._data)
