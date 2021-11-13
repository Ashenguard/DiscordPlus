from typing import Optional, Union, Callable

from discord import Message, Color
from discord.ext.commands import Bot, DefaultHelpCommand

from discordplus.lib import Config, RequiredValue


class SlashConfig(Config, auto_setup=True):
    sync_commands: bool = False
    debug_guild: Optional[int] = None
    delete_from_unused_guilds: bool = False
    sync_on_cog_reload: bool = False
    override_type: bool = False
    application_id: Optional[int] = None


class BotPlusConfig(Config, auto_setup=True):
    token: str = RequiredValue()
    command_prefix: Union[str, Callable[[Bot, Message], str]] = None
    log_channel_id: int = None
    help_command = DefaultHelpCommand()
    description = None
    color = Color.default()

    slash_config: Optional[SlashConfig] = None
