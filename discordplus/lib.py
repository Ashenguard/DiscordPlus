import inspect
import re
import sys
import traceback
from typing import Union, Callable, Any, Iterable, Dict

from discord import Embed, Color, Message
from discord.abc import Messageable

__all__ = ['ExceptionValue', 'ExceptionFormat',
           'extract_number', 'async_wrapper', 'ghost_ping',
           'try_except', 'try_delete', 'try_send', 'try_add_reaction']

from discordplus.errors import ExpectedValue
from discordplus.extra import Pingable


class ExceptionValue:
    def __init__(self, exception: Exception):
        self._exception = exception

    @property
    def exception(self):
        return self._exception

    @property
    def format(self):
        return ExceptionFormat(self.exception)


class ExceptionFormat:
    def __init__(self, exception: Exception, *details):
        self._exception = exception
        self._trace = ExceptionFormat._format(exception)
        self.details = details

    @property
    def name(self):
        return self._exception.__class__.__name__

    @property
    def traceback(self):
        return self._trace

    @property
    def exception(self):
        return self._exception

    @property
    def message(self):
        return str(self._exception).capitalize()

    @property
    def embed(self):
        embed = Embed(title=':warning: Exception', description=f'**Exception:** `{self.name}`\n**Description:**\n{self.message}\n\n**Traceback**:\n```py\n{self.traceback}```', colour=Color.red())
        if self.details is not None and len(self.details) > 0:
            embed.add_field(name='Provided Information:', value='\n'.join(self.details))
        return embed

    @property
    def premessage(self):
        from discordplus import PreMessage
        return PreMessage(embed=self.embed)

    def print(self, message='Execute failed'):
        print(f'{message} due {self.name}:')
        print(self.traceback)

    @staticmethod
    def _format(exception: Exception) -> str:
        exception_list = traceback.format_stack()
        exception_list = exception_list[:-2]
        exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
        exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
        return "".join(exception_list)[:-1]


class RequiredValue:
    pass


class Config:
    __options: Dict[str, Any] = {}

    _extra = {}

    def __init__(self, **options):
        for k, v in self.__options.items():
            value = options.pop(k, v)
            if isinstance(value, RequiredValue):
                raise ExpectedValue(f"A value for '{k}' is required")
            setattr(self, k, value)
        self._extra = options.copy()

    def __init_subclass__(cls, **kwargs):
        if kwargs.get('auto_setup', False) is True:
            attrs = (attr for attr in dir(cls) if not attr.startswith("_"))
            options = {}
            for attr in attrs:
                if attr in ('options', 'extra_options', 'all'):
                    continue
                options[attr] = getattr(cls, attr)

            setattr(cls, f'_{cls.__name__}__options', options)

    @property
    def options(self):
        return {k: getattr(self, k, v) for k, v in self.__options.items()}

    @property
    def extra_options(self):
        return self._extra

    @property
    def all(self):
        return {**self.options, **self._extra}


def extract_number(text, required_pattern='\d+', cast_float: bool = False) -> Union[int, float]:
    if text is None:
        return 0
    try:
        cast = float if cast_float else int
        match = re.findall(required_pattern, text)[0]
        number = re.findall('\d+', match)[0]
        return cast(number)
    except Exception:
        return 0


def async_wrapper(func):
    if inspect.iscoroutinefunction(func):
        return func

    async def wrap(*args, **kwargs):
        return func(*args, **kwargs)

    return wrap


async def try_except(method: Callable, *args, **kwargs):
    method = async_wrapper(method)
    try:
        return await method(*args, **kwargs)
    except Exception as error:
        return ExceptionValue(error)


async def try_delete(message: Message, delay: int = 0):
    return not isinstance(await try_except(message.delete, delay=delay), ExceptionValue)


async def try_send(ctx: Messageable, content=None, *, tts=None, embed=None, embeds=None, file=None, files=None, stickers=None, delete_after=None, nonce=None, allowed_mentions=None, reference=None, mention_author=None, view=None, premessage=None):
    if premessage is None:
        message = await try_except(ctx.send, content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author)
    else:
        message = await try_except(premessage.send, ctx)
    return None if isinstance(message, ExceptionValue) else message


async def ghost_ping(ctx: Messageable, pingable: Pingable):
    await try_delete(await try_send(ctx, pingable.mention))


async def try_add_reaction(message: Message, emotes: Union[Iterable[Any], Any]):
    try:
        for e in emotes:
            await try_except(message.add_reaction, e)
    except TypeError:
        await try_except(message.add_reaction, emotes)
