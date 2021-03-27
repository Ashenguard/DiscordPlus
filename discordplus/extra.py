from sys import version_info
from typing import Union

from discord import DMChannel, TextChannel, GroupChannel, Role, Member, User
from discord.abc import User as ABCUser
from requests import __version__ as __requests_version__


# Special variables
__version__ = '0.0.1'
__agent__ = f'DiscordPlus (https://github.com/ashenguard/discord-plus {__version__}) Python/{version_info[0]}.{version_info[1]} requests/{__requests_version__}'

# Custom typings
MessageChannel = Union[DMChannel, TextChannel, GroupChannel]
Pingable = Union[User, Member, Role, ABCUser]
