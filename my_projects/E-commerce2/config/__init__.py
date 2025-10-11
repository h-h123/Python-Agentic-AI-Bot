import os
from configparser import ConfigParser

class Config:
    def __init__(self, env='development'):
        self.config = ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        self.env = env.lower()

        if self.env not in self.config:
            raise ValueError(f"Environment '{self.env}' not found in config.ini")

        self._load_config()

    def _load_config(self):
        for key, value in self.config[self.env].items():
            if value.lower() in ('true', 'false'):
                value = self.config[self.env].getboolean(key)
            elif value.isdigit():
                value = self.config[self.env].getint(key)
            setattr(self, key.upper(), value)

    def get(self, key, default=None):
        return getattr(self, key.upper(), default)

config = Config(os.getenv('FLASK_ENV', 'development'))