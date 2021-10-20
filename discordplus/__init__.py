from .classes import BotPlus, CogPlus, PreMessage, BotPlusConfig, SlashConfig
from .lib import try_except, try_send, try_delete, try_add_reaction, async_wrapper, ExceptionValue, ExceptionFormat, ghost_ping, extract_number
from .task import TaskPlus, TaskPlusStatus


# Doing overrides without affecting the import
def _overrides():
    from discord.ext.commands import Cog

    # CogPlus update
    @property
    def CP_is_beta(self) -> bool:
        return hasattr(self, '__beta__') and self.__beta__

    @property
    def CP_is_disabled(self) -> bool:
        return hasattr(self, '__disabled__') and self.__disabled__

    Cog.is_beta = CP_is_beta
    Cog.is_disabled = CP_is_disabled


_overrides()
