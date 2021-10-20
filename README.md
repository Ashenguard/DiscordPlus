![](https://img.shields.io/badge/dynamic/json?color=green&label=build&query=status&url=https%3A%2F%2Fjitpack.io%2Fapi%2Fbuilds%2Fcom.github.Ashengaurd%2FDiscordPlus%2FlatestOk)
![](https://img.shields.io/github/license/Ashengaurd/DiscordPlus)
![](https://img.shields.io/github/v/release/Ashengaurd/DiscordPlus)
![](https://img.shields.io/github/downloads/Ashengaurd/DiscordPlus/total)
[![Discord](https://img.shields.io/discord/690930221930643467?label=discord)](https://discord.gg/6exsySK)
# Discord Plus
This library is additional tools for python discord developers where they can reduce the effort they need to develop a bot.  
This library contains tools, database and pre-made commands and events.

> **Note:** This is still under development, But it is usable. 

## How to install
To install just use following command
```shell
pip install discordplus
```
This library will have dev/beta builds on the github, to install them you can use
```shell
pip install --upgrade git+https://github.com/Ashengaurd/DiscordPlus.git
```
***
By installing this library following libraries and their dependencies will be installed too.
> Discord.py  
> Flask - Used for web API  
> Requests - Used for posting data on top.gg  
> Json & Yaml - Used as Not SQL Database managers

# Simple Examples
`BotPlus` extended class of Bot  
`Premessage` a message ready to be sent
```python
from discordplus import BotPlus, PreMessage

bot = BotPlus('!', log_channel_id=1234567890)

## Library which has several useful cogs and listeners and you can activate them
bot.library.activate_prefix_send_on_ping()
bot.library.activate_api(__name__, host='0.0.0.0', port=8080, vote_auth='It is valid')
bot.library.activate_topgg_poster('TopGGLongAPITokenWhichYouNeverShareWithAnyIndividual')

## Load all extensions recursive
bot.load_extensions('./cogs', './cogs_part_2')

## Vote event
@bot.event
async def vote(data):
    premessage = PreMessage(f'User {data["user"]} has voted!')
    await bot.log(premessage)

## Anything else you will do with a simple bot including run it :)
```
`CogPlus` extended class of Cog with tags

```python
from discordplus import CogPlus, BotPlus


@CogPlus.beta
class beta_cog(CogPlus):
    """A Beta cog which will be loaded"""
    pass


@CogPlus.beta
@CogPlus.disabled
class disabled_beta_cog(CogPlus):
    """A Disabled Beta cog which will not be loaded"""
    pass


@CogPlus.disabled
class disabled_cog(CogPlus):
    """A Disabled cog which will not be loaded"""
    pass


class cog(CogPlus):
    """A normal cog which will be loaded"""
    pass

    
def setup(bot: BotPlus):
    bot.add_cog(beta_cog())           # Will warn and load
    bot.add_cog(disabled_cog())       # Will warn and skip
    bot.add_cog(disabled_beta_cog())  # Will warn and skip
    bot.add_cog(cog())                # Just loads ;)
```
Emoji library with all emojis in discord:
```python
from discordplus.emotes import *

...

async def bar(channel):
    await channel.send(People.get('smile'))  # All categories of discord official emojis
    await channel.send(Emotes.grinning)      # Emotes contains all useful emojis as variables for easier access
    await channel.send(Emotes.numbers[1])    # All 10 emojis of numbers accessible
    await channel.send(Emotes.letters['a'])  # All 26 emojis of letters accessible
```