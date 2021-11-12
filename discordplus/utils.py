import inspect

from discord.abc import Messageable
from discord_slash.context import InteractionContext

message_args = []
_temp_args = inspect.getfullargspec(Messageable.send)
for _arg in _temp_args.args + _temp_args.kwonlyargs:
    if _arg != 'self':
        message_args.append(_arg)

interaction_args = []
_temp_args = inspect.getfullargspec(InteractionContext.send)
for _arg in _temp_args.args + _temp_args.kwonlyargs:
    if _arg != 'self':
        interaction_args.append(_arg)


message_args = set(message_args)
interaction_args = set(interaction_args)
