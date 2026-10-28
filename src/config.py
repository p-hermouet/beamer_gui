from pathlib import Path
import tomllib


APP_PATH = Path(__file__).parent.parent
TMP_PATH = APP_PATH / 'tmp'
TEMPLATES_PATH = APP_PATH / 'templates'
CONFIG_PATH = APP_PATH / 'config.toml'

LOCAL_PATH = Path('.beamer_gui')
LOCAL_CFG = LOCAL_PATH / 'config.toml'
LOCAL_TEX = LOCAL_PATH / 'tex'


class Config:
    def __init__(self):
        self.cfg = tomllib.loads(CONFIG_PATH.read_text()) # TODO raise error if any issue

    def __getitem__(self, key):
        return self.cfg[key]


cfg = Config()
