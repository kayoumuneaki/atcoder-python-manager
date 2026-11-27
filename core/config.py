import json
from pathlib import Path

# 起動フォルダに関係なく project/config.json を使う
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


class Config:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path or DEFAULT_CONFIG_PATH)

    def load(self):
        if not self.config_path.exists():
            return {}

        try:
            with self.config_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except json.JSONDecodeError:
            return {}

    def save(self, settings):
        with self.config_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                settings,
                file,
                ensure_ascii=False,
                indent=4
            )