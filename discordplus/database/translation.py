import json
from typing import Dict, Any, Union
from warnings import warn

from discord import Embed
from discord.abc import Messageable
from discord_slash.context import InteractionContext

from .database import YAMLDatabase
from ..classes import BotPlus, PreMessage
from ..utils import message_args


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


def data_to_dict(bot, data, **kwargs):
    color = kwargs.pop('color', bot.color)
    embed = {'type': 'rich', 'color': color.value}
    for key, item in data.items():
        embed[key.lower()] = item

    if 'fields' in embed.keys():
        fields = embed['fields']
        for field in fields:
            if 'inline' not in field.keys():
                field['inline'] = False

    return Embed.from_dict(embed)


class Translation(YAMLDatabase):
    def __init__(self, bot: BotPlus, file: str, language: str = 'EN'):
        super().__init__(f'./translations/{language}/{file.lower()}.yml')
        self.bot = bot

    def get(self, path, **kwargs):
        value = self.get_data(path)
        if type(value) == str:
            value = set_placeholders(value, **kwargs)
        return value

    def __getitem__(self, item):
        return self.get(item)

    def get_json_translated(self, path: str = None, **kwargs):
        string = json.dumps(self.get(path))
        string = set_placeholders(self.bot, string, **kwargs)
        return json.loads(string, strict=False)

    def get_embed(self, path: str = None, **kwargs) -> Embed:
        warn('`Translation#get_embed` is deprecated. Please use `Translation#get_premessage`', DeprecationWarning)
        data: Dict[str, Any] = self.get_json_translated(path, **kwargs)
        return data_to_dict(self.bot, data, **kwargs)

    def get_premessage(self, ctx: Union[Messageable, InteractionContext], path: str = None, **kwargs) -> PreMessage:
        send_args = {}
        for key in message_args:
            send_args[key] = kwargs.get(key, None)

        value = self.get_json_translated(path, **kwargs)
        if isinstance(value, dict):
            if 'content' in value.keys():
                for key in message_args:
                    if key in value.keys():
                        send_args[key] = kwargs.get(key, None)
            else:
                send_args['embed'] = value
        else:
            send_args['content'] = str(value)

        if isinstance(send_args['embed'], dict):
            send_args['embed'] = data_to_dict(self.bot, send_args['embed'], **kwargs)

        return PreMessage(**kwargs)
