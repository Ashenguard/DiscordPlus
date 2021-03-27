from .classes import BotPlus, CogPlus, PreMessage
from .task import TaskPlus, TaskPlusStatus
from .lib import *


# Doing overrides without affecting the import
def _overrides():
    import discord
    import re

    send_method = discord.abc.Messageable.send
    doc = send_method.__doc__.splitlines(False)
    index = [i for i, item in enumerate(doc) if re.search('\s*?Raises\s*', item)][0]
    doc.insert(index, 'premessage: Optional[:class:`~discordplus.PreMessage`]\n\tIf set, will send the premessage instead.')

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=None, reference=None, mention_author=None, premessage=None):
        if premessage is not None:
            return await premessage.send(self)
        else:
            return await send_method(self, content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author)

    send.__doc__ = "\n".join(doc)
    discord.abc.Messageable.send = send

_overrides()