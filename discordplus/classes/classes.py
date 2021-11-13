import os
from typing import Union, List, Dict

from discord.ext.commands import Bot, Cog, ExtensionAlreadyLoaded
from discord_slash import SlashCommand
from discord_slash.cog_ext import cog_slash

from discordplus import PreMessage
from discordplus.lib import ExceptionFormat
from .configs import BotPlusConfig


class BotPlus(Bot):
    def __init__(self, config: BotPlusConfig):
        super().__init__(
            command_prefix=config.command_prefix,
            help_command=config.help_command,
            description=config.description,
            **config.extra_options
        )
        self._token = config.token
        self.log_channel_id = config.log_channel_id
        self.color = config.color

        slash_config = config.slash_config
        self._slash = None
        if slash_config is not None:
            self._slash = SlashCommand(self, **slash_config.options)

        from ..coglib import CogLib
        self._library = CogLib(self)

        self.api = None
        self.__disabled_cogs__ = []
        self.__beta_cogs__ = []

    @property
    def library(self):
        return self._library

    def get_slash(self):
        return self._slash

    def slash_command(self, *, name: str = None, description: str = None, guild_ids: List[int] = None, options: List[dict] = None, default_permission: bool = True, permissions: dict = None, connector: dict = None):
        return self._slash.slash(name=name, description=description, guild_ids=guild_ids, options=options, default_permission=default_permission, permissions=permissions, connector=connector)

    async def log(self, premessage: PreMessage):
        channel = self.get_channel(self.log_channel_id)
        return await premessage.try_send(channel)

    async def log_exception(self, exception: Exception, *details: str):
        return await self.log(ExceptionFormat(exception, *details).premessage)

    def load_extensions(self, *files: str):
        for file in files:
            if not os.path.exists(file):
                continue
            if any(part.startswith('_') for part in file.replace('\\', '/').split('/')):
                continue
            if os.path.isdir(file):
                within_files = [f'{file}/{within_file}' for within_file in os.listdir(file)]
                self.load_extensions(*within_files)
            else:
                path = file.replace('/', '.').replace('\\', '.')
                if path.endswith('.py'):
                    path = path[:-3]

                try:
                    self.load_extension(path)
                except ExtensionAlreadyLoaded:
                    self.reload_extension(path)

    @property
    def cogs_status(self):
        cogs = [(name, CogPlus.Status.BetaEnabled if hasattr(cog, '__beta__') and cog.__beta__ else CogPlus.Status.Enabled)
                for name, cog in self.cogs.items()]
        cogs.extend([(cog.qualified_name, CogPlus.Status.BetaDisabled if hasattr(cog, '__beta__') and cog.__beta__ else CogPlus.Status.Disabled)
                     for cog in self.__disabled_cogs__])
        return dict(cogs)

    def add_cog(self, cog, *, override: bool = False):
        if hasattr(cog, '__disabled__') and cog.__disabled__:
            if cog not in self.__disabled_cogs__:
                self.__disabled_cogs__.append(cog)
                print(f'"{cog.qualified_name}" is tagged disabled.')
            return

        # Todo - dpy 2.0 - Add override to add_cog
        super(BotPlus, self).add_cog(cog)
        if hasattr(cog, '__beta__') and cog.__beta__:
            self.__beta_cogs__.append(cog)
            print(f'"{cog.qualified_name}" is tagged beta but it has been activated')

    def run(self):
        return super(BotPlus, self).run(self._token)

    def get_translation_dict(self) -> Dict[str, str]:
        return {'Bot': self.user.mention, 'BotID': self.user.id, 'Prefix': self.command_prefix, 'Guilds': len(self.guilds), 'Users': len(self.users)}


class CogPlus(Cog):
    __disabled__ = False
    __beta__ = False

    class Status:
        BetaDisabled = 'BetaDisabled'
        BetaEnabled = 'BetaEnabled'
        Disabled = 'Disabled'
        Enabled = 'Enabled'

    def __init__(self, bot: BotPlus):
        self.bot = bot

    @staticmethod
    def slash_command(*, name: str = None, description: str = None, guild_ids: List[int] = None, options: List[dict] = None, default_permission: bool = True, permissions: dict = None, connector: dict = None):
        return cog_slash(name=name, description=description, guild_ids=guild_ids, options=options, default_permission=default_permission, permissions=permissions, connector=connector)

    # Decorators
    @staticmethod
    def disabled(cls):
        if issubclass(cls, CogPlus):
            cls.__disabled__ = True
        else:
            raise TypeError(f'CogPlus.disabled only accept a sub-class of "CogPlus" not a "{type(cls)}"')
        return cls

    @staticmethod
    def beta(cls):
        if issubclass(cls, CogPlus):
            cls.__beta__ = True
        else:
            raise TypeError(f'CogPlus.disabled only accept a sub-class of "CogPlus" not a "{type(cls)}"')
        return cls


class CommandPlus:
    name: str = None
    description: str = None
    guild_ids: List[int] = None
    options: List[dict] = None
    default_permission: bool = True
    permissions: dict = None
    connector: dict = None

    def __init__(self, cog: CogPlus, base: Union['CommandGroupPlus', 'BaseCommandPlus'] = None):
        self.cog = cog
        self.base = base

    def register(self):
        cmd = getattr(self, 'slash_command', None)
        if cmd is None:
            raise NotImplementedError

        if isinstance(self.base, CommandGroupPlus):
            wrapper = self.cog.bot.get_slash().subcommand(
                base=self.base.base.name,
                subcommand_group=self.base.name,
                name=self.name,
                description=self.description,
                base_description=self.base.base.description,
                base_default_permission=self.base.base.default_permission,
                base_permissions=self.base.base.permissions,
                subcommand_group_description=self.base.description,
                guild_ids=self.guild_ids,
                options=self.options,
                connector=self.connector,
            )
        elif isinstance(self.base, BaseCommandPlus):
            wrapper = self.cog.bot.get_slash().subcommand(
                base=self.base.name,
                name=self.name,
                description=self.description,
                base_description=self.base.description,
                base_default_permission=self.base.default_permission,
                base_permissions=self.base.permissions,
                guild_ids=self.guild_ids,
                options=self.options,
                connector=self.connector,
            )
        else:
            wrapper = self.cog.bot.get_slash().slash(
                name=self.name,
                description=self.description,
                guild_ids=self.guild_ids,
                options=self.options,
                default_permission=self.default_permission,
                permissions=self.permissions,
                connector=self.connector
            )

        return wrapper(cmd)


class BaseCommandPlus(CommandPlus):
    name: str = None
    description: str = None
    default_permission: bool = True
    permissions: dict = None


class CommandGroupPlus(CommandPlus):
    name: str = None
    description: str = None
