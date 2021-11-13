import json

from .database import YAMLDatabase
from ..classes import BotPlus, PreMessage


class TranslationError(Exception):
    """
    This error will be raised if translation is malformed
    """


def set_placeholders(bot: BotPlus, string: str, escape=True, case_sensitive=False, **kwargs) -> str:
    if type(string) != str:
        return string

    for k, v in (*bot.get_translation_dict().items(), *{k.lower(): v for k, v in kwargs.items()}.items()):
        v = str(v).replace("\\", "\\\\").replace("\"", "\\\"") if escape else str(v)
        string = string.replace('{' + k + '}', v)

    return string


class Translation(YAMLDatabase):
    def __init__(self, bot: BotPlus, file: str, language: str = 'EN'):
        super().__init__(f'./translations/{language}/{file.lower()}.yml')
        self.bot = bot

    def get(self, path, **kwargs):
        value = self.get_data(path)
        if isinstance(value, str):
            value = set_placeholders(self.bot, value, **kwargs)

        return value

    def __getitem__(self, item):
        return self.get_data(item)

    def get_json_translated(self, path: str = None, **kwargs):
        string = json.dumps(self.get(path))
        string = set_placeholders(self.bot, string, **kwargs)
        return json.loads(string, strict=False)

    def get_premessage(self, path: str = None, **kwargs) -> PreMessage:
        value = self.get_json_translated(path, **kwargs)
        return PreMessage.from_data(self.bot, value, **kwargs)
