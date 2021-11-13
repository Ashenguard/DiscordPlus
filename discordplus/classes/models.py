from typing import Union, Optional

from discord import Message, Embed
from discord.abc import Messageable
from discord_slash.context import InteractionContext

from ..lib import try_except

messageable_args = {'content': None, 'tts': False, 'embed': None, 'file': None, 'files': None, 'nonce': None, 'delete_after': None, 'allowed_mentions': None, 'reference': None, 'mention_author': None}
interaction_args = {'content': None, 'tts': False, 'embed': None, 'embeds': None, 'file': None, 'files': None, 'delete_after': None, 'allowed_mentions': None, 'hidden': False, 'components': None}
_all_args = {**messageable_args, **interaction_args}


def _data_to_embed(bot, data):
    embed = {'type': 'rich', 'color': bot.color.value}
    for key, item in data.items():
        embed[key.lower()] = item

    if 'fields' in embed.keys():
        fields = embed['fields']
        for field in fields:
            if 'inline' not in field.keys():
                field['inline'] = False

    return Embed.from_dict(embed)


class PreMessage:
    def __init__(self, **kwargs):
        self.interaction_args = {}
        self.messageable_args = {}

        for k, v in messageable_args.items():
            self.messageable_args[k] = kwargs.get(k, v)

        for k, v in interaction_args.items():
            self.interaction_args[k] = kwargs.get(k, v)

        self._message = None

    @staticmethod
    def from_data(bot, data: Union[str, dict], **kwargs) -> 'PreMessage':
        if isinstance(data, str):
            return PreMessage(content=data, **kwargs)
        elif isinstance(data, dict):
            data = {k.lower(): v for k, v in (*data.items(), *kwargs.items())}
            embed = Embed.from_dict({**data, 'color': bot.color})
            embed_is_empty = True
            for k, v in embed.to_dict().items():
                if k not in ['color', 'colour', 'type'] and v:
                    embed_is_empty = False
                    break

            if not embed_is_empty:
                data['embed'] = embed

            return PreMessage(**data)
        else:
            raise TypeError('only `str` or `dict` is accepted')

    @property
    def message(self) -> Optional[Message]:
        return self._message

    def copy(self) -> 'PreMessage':
        copy = PreMessage()
        copy.messageable_args = self.messageable_args.copy()
        copy.interaction_args = self.interaction_args.copy()

        return copy

    async def send(self, ctx: Union[Messageable, InteractionContext]):
        if isinstance(ctx, InteractionContext):
            args = self.interaction_args
        else:
            args = self.messageable_args
        return await ctx.send(**args)

    async def try_send(self, ctx: Messageable):
        return await try_except(self.send, ctx)
