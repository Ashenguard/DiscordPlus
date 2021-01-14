import importlib

import asyncio
import discord
import os
from discord.ext import commands
from typing import Optional, Union

from discordplus.lib import format_exception


class BotPlus(commands.Bot):
    def __init__(self, command_prefix, log_channel_id=None, help_command=commands.DefaultHelpCommand(), description=None, **options):
        super().__init__(command_prefix=command_prefix, help_command=help_command, description=description, **options)
        self.log_channel_id = log_channel_id

    async def try_delete(self, message: discord.Message, delay: Optional[float] = None) -> bool:
        try:
            await message.delete(delay=delay)
            return True
        except Exception:
            return False

    async def try_send(self, ctx: discord.abc.Messageable, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=None):
        try:
            return await ctx.send(content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions)
        except Exception:
            return None

    async def ghost_ping(self, ctx: discord.abc.Messageable, ping: Union[discord.Role, discord.User]):
        try:
            message = await self.try_send(ctx, ping.mention)
            await self.try_delete(message)
        except Exception:
            pass

    async def handle_exception(self, exception: Exception, *details: str):
        name = exception.__class__.__name__
        trace = format_exception(exception)
        desc = str(exception).capitalize()
        embed = discord.Embed(title=':warning: Exception', description=f'**Exception:** `{name}`\n**Description:**\n{desc}\n\n**Traceback**:\n```py\n{trace}```', colour=discord.Color.red())
        if details is not None and len(details) > 0:
            embed.add_field(name='Provided Information:', value='\n'.join(details))

        return await self.log(embed=embed)

    async def confirm(self, channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel], user: discord.User, embed: discord.Embed, timeout: Optional[int] = None, delete_after: bool = False) -> Optional[bool]:
        emoji = await self.get_reaction(channel, user, embed, timeout, delete_after, ['✅', '❌'])
        return None if emoji is None else emoji == '✅'

    async def get_reaction(self, channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel], user: discord.User, embed: discord.Embed, timeout: Optional[int] = None, delete_after: bool = False, emotes: list = None) -> Optional[str]:
        emoji = None
        message: discord.Message = await channel.send(embed=embed)
        if emotes is not None:
            for emoji in emotes:
                await message.add_reaction(emoji)

        try:
            event = await self.wait_for('reaction_add', check=self.check_reaction(message, user, emotes), timeout=timeout)
            emoji = event[0].emoji
        finally:
            if delete_after:
                await self.try_delete(message)
            else:
                await message.clear_reactions()

            return emoji

    async def get_answer(self, channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel], user: discord.User, embed: discord.Embed, timeout: Optional[int] = None, delete_after: bool = False) -> Optional[str]:
        content = None
        message: discord.Message = await channel.send(embed=embed)
        respond = None

        try:
            respond = await self.wait_for('message', check=self.check_message(user, channel), timeout=timeout)
            content = respond.content
        finally:
            if delete_after:
                await self.try_delete(message)
                await self.try_delete(respond)

            return content

    def check_message(self, author: discord.User, channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel], forbid: bool = False):
        def check(message: discord.Message):
            if forbid and message.channel.id == channel.id and message.author.id != author.id and message.author.id != self.user.id:
                embed = discord.Embed(title='**ERROR**', description=f'Only {author.mention} can send message here', colour=discord.Colour.red())
                asyncio.ensure_future(message.delete())
                asyncio.ensure_future(channel.send(embed=embed, delete_after=20))

            return message.author.id == author.id and channel.id == message.channel.id

        return check

    def check_reaction(self, target: discord.Message, author: discord.User, emotes: list = None):
        def check(c_reaction: discord.Reaction, c_user):
            message: discord.message = c_reaction.message
            if message.id == target.id and c_user.id != self.user.id:
                asyncio.ensure_future(c_reaction.remove(c_user))

            if c_user != author or message.id != target.id:
                return False
            return emotes is None or len(emotes) == 0 or str(c_reaction.emoji) in emotes

        return check

    async def log(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=None):
        channel = self.get_channel(self.log_channel_id)
        await self.try_send(channel, content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions)

    def load_extensions_from_folder(self, folder: str):
        within_files = [f'{folder}/{within_file}' for within_file in os.listdir(folder)]
        self.load_extensions(*within_files)

    def load_extensions(self, *files: str):
        for file in files:
            if os.path.isdir(file):
                self.load_extensions_from_folder(file)
            else:
                importlib.import_module(file.replace('/', '.').replace('\\', '.'))

    @property
    def cogs_status(self):
        cogs = [(name, CogPlus.Status.BetaEnabled if hasattr(cog, '__beta__') and cog.__beta__ else CogPlus.Status.Enabled)
                for name, cog in self.cogs.items()]
        cogs.extend([(cog.qualified_name, CogPlus.Status.BetaDisabled if hasattr(cog, '__beta__') and cog.__beta__ else CogPlus.Status.Disabled)
                     for cog in self.__disabled_cogs])
        return dict(cogs)

    # Decorators
    __disabled_cogs = []

    def load_cog(self, cls):
        if issubclass(cls, CogPlus):
            cog = cls(self)
            if cog.__disabled__:
                self.__disabled_cogs.append(cog)
            else:
                self.add_cog(cog)
        else:
            raise TypeError(f'BotPlus.cog only accept a sub-class of "CogPlus" not a "{type(cls)}"')


class CogPlus(commands.Cog):
    __disabled__ = False
    __beta__ = False

    def __init__(self, bot: BotPlus):
        self.bot = bot

    class Status:
        BetaDisabled = 'BetaDisabled'
        BetaEnabled = 'BetaEnabled'
        Disabled = 'Disabled'
        Enabled = 'Enabled'

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
