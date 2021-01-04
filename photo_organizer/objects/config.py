import varyaml
from pathlib import Path


class Config(object):
    def __init__(self, config_dict):
        self.jpeg_extension = config_dict.get("jpeg_extension")
        self.raw_extension = config_dict.get("raw_extension")
        self.input_directory = config_dict.get("input_directory")
        self.raw_backup_directory = config_dict.get("save_directory").get("raw_for_backup")
        self.raw_edit_directory = config_dict.get("save_directory").get("raw_for_edit")
        self.jpeg_directory = config_dict.get("save_directory").get("jpeg")
        self.delete_directory = config_dict.get("delete_directory")

        assert self.jpeg_extension is not None, "`jpeg_extension` is mandatory in config"
        assert self.raw_extension is not None, "`raw_extension` is mandatory in config"
        assert Path(self.raw_backup_directory).exists(), "No such save directory for `raw_for_backup`"
        assert Path(self.raw_edit_directory).exists(), "No such save directory for `raw_for_edit`"
        assert Path(self.jpeg_directory).exists(), "No such save directory for `jpeg`"
        assert Path(self.delete_directory).exists(), "No such `delete_directory`"


def read_config(config_filename: str):
    with open(config_filename, "r") as f:
        config_dict = varyaml.load(f)
        return Config(config_dict)
