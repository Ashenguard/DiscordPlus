import traceback
from io import StringIO
from typing import Union

from discord import Color, File
from discord.ext.commands import Context
from discord_slash import SlashContext
from discord_slash.error import SlashCommandError

from .classes import BotPlus
from .database.translation import Translation
from .utils import message_args


class InteractionError(Exception):
    """
    A normal exception for commands to raise which should be handled by bot
    """
    _name = None
    _args = ()

    async def send(self, bot: BotPlus, ctx: Union[Context, SlashContext], translation: Translation = None):
        if self._name is None:
            return
        kwargs = {arg: getattr(self, arg, '-') for arg in self._args}
        await self.send_error(bot, ctx, self._name, translation, **kwargs)

    async def send_error(self, bot, ctx, error_name, translation: Translation = None, **kwargs):
        if translation is None:
            translation = Translation(bot, "Errors", "EN")

        send_args = {}
        for arg in message_args:
            send_args[arg] = kwargs.pop(arg, None)

        embed = translation.get_premessage(error_name, colot=Color.red(), **kwargs)
        await ctx.send(embed=embed, **send_args, hidden=True)


class UnexpectedError(InteractionError):
    """
    Raises when another exception happens unintentionally
    """
    _name = 'Unexpected'
    _args = ('name', 'message', 'file')

    def __init__(self, exception: Exception):
        self.name = exception.__class__
        self.message = str(exception)

        trace = traceback.format_list(traceback.extract_tb(exception.__traceback__))

        buf = StringIO()
        buf.write(''.join(trace))
        buf.seek(0)
        self.file = File(buf, filename='traceback.txt')


class ExpectedValue(ValueError):
    pass


class ComponentError(SlashCommandError):
    pass


class IncorrectFormatError(ComponentError):
    pass


class IncorrectTypeError(ComponentError):
    pass
