import json_config


class Utils:
    @staticmethod
    def read_config():
        config = json_config.connect('config.json')
        return config
