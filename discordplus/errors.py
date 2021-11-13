import traceback
from io import StringIO
from typing import Union

from discord import Color, File
from discord.ext.commands import Context
from discord_slash import SlashContext
from discord_slash.error import SlashCommandError

from .classes import BotPlus
from .database.translation import Translation


class InteractionError(Exception):
    """
    A normal exception for commands to raise which should be handled by bot
    """
    _name = None
    _args = ()

    async def send(self, bot: BotPlus, ctx: Union[Context, SlashContext], translation: Translation = None):
        if self._name is None:
            raise ValueError('The InteractionError `name` can not be null')

        if isinstance(self._args, dict):
            kwargs = {arg: getattr(self, arg, val) for arg, val in self._args.items()}
        else:
            kwargs = {arg: getattr(self, arg, None) for arg in self._args}

        if translation is None:
            translation = Translation(bot, "Errors", "EN")

        premessage = translation.get_premessage(self._name, color=Color.red(), hidden=True, **kwargs)
        print(premessage.interaction_args)
        await premessage.send(ctx)


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


class ComponentError(SlashCommandError):
    pass


class IncorrectFormatError(ComponentError):
    pass


class IncorrectTypeError(ComponentError):
    pass
