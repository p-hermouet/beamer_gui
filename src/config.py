from pathlib import Path
import tomllib


CONFIG_PATH = Path('config.toml')


class Config:
    def __init__(self):
        self.cfg = tomllib.loads(CONFIG_PATH.read_text()) # TODO raise error if any issue

    def __getitem__(self, key):
        return self.cfg[key]


cfg = Config()
