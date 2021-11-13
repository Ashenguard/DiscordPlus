from typing import Union, Optional

from discord import Message
from discord.abc import Messageable
from discord_slash.context import InteractionContext

from discordplus import try_except

messageable_args = {'content': None, 'tts': False, 'embed': None, 'file': None, 'files': None, 'nonce': None, 'delete_after': None, 'allowed_mentions': None, 'reference': None, 'mention_author': None}
interaction_args = {'content': None, 'tts': False, 'embed': None, 'embeds': None, 'file': None, 'files': None, 'delete_after': None, 'allowed_mentions': None, 'hidden': False, 'components': None}


class PreMessage:
    def __init__(self, **kwargs):
        self.interaction_args = {}
        self.messageable_args = {}

        for k, v in messageable_args.items():
            self.messageable_args[k] = kwargs.get(k, v)

        for k, v in interaction_args.items():
            self.interaction_args[k] = kwargs.get(k, v)

        self._message = None

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
