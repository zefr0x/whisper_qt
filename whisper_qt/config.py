"""Manage config and prefrences."""
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from .default_files import xdg_config_file


class Config:
    """Read and write config from and to INI config file."""

    def __init__(self, config_file_path: Optional[Path] = None) -> None:
        """Initilize the object with the config path and config parser object."""
        self.config_file_path = config_file_path or xdg_config_file()

        # Create the config parser object.
        self.__config = ConfigParser()

    def read_config(self) -> None:
        """Read the config file to the memory."""
        # If file doesn't exist nothing will happen.
        self.__config.read(self.config_file_path)

    def set_option(self, section: str, option: str, value: Optional[str]) -> None:
        """Add or update an optin in the config object."""
        if not self.__config.has_section(section):
            self.__config.add_section(section)

        self.__config.set(section, option, value)

    def get_option(self, section: str, option: str) -> Optional[str]:
        """Get the string value of an option."""
        if section in self.__config.sections():
            return self.__config.get(section, option)
        return None

    def write_config(self) -> None:
        """Write to the config file."""
        # Create the parent directory if it doesn't exits, else don't do anything.
        Path.mkdir(self.config_file_path.parent, parents=True, exist_ok=True)

        with open(self.config_file_path, "w") as file:
            self.__config.write(file)
