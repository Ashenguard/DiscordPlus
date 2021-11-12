from abc import ABC
from asyncio import TimeoutError, ensure_future
from enum import Enum
from typing import Union, Coroutine, Any, Callable, NoReturn

from discord import Message, User
from discord.ext.commands import Context
from discord_slash import SlashContext, ButtonStyle, ComponentContext

from .ineractions import Button
from ..classes import BotPlus
from ..errors import InteractionError


class DynamicRequestError(InteractionError):
    _name = 'DynamicRequest'


class DynamicRequestTypeError(DynamicRequestError):
    _name = 'DynamicRequestType'
    _args = ('type',)

    def __init__(self, required_type):
        self.type = required_type


class RequestEvent(str, Enum):
    Component = 'component'
    Message = 'message'
    Reaction = 'reaction'


class RequestAction(Enum):
    Repeat = 0
    End = 1


class DynamicRequest:
    def __init__(self, bot: BotPlus, event: RequestEvent, ctx: Union[Context, SlashContext], target: User, timeout: int = 300):
        self.bot = bot
        self.interaction = event
        self.ctx = ctx
        self.target = target
        self.timeout = timeout
        self._result = None

    def set_result(self, value):
        self._result = value

    def get_result(self):
        return self._result

    def check(self, ctx) -> bool:
        raise NotImplementedError

    async def handle_request(self) -> Message:
        raise NotImplementedError

    async def handle_timeout(self) -> NoReturn:
        raise NotImplementedError

    async def handle_event(self, event) -> RequestAction:
        raise NotImplementedError

    async def execute(self):
        self.request_message = None
        self.request_message = await self.handle_request()

        while True:
            try:
                event = await self.bot.wait_for(self.interaction, check=self.check, timeout=self.timeout)
                result = await self.handle_event(event)

                if result == RequestAction.End:
                    break
            except TimeoutError:
                await self.handle_timeout()
                break


class DynamicButton(Button):
    def __init__(self, button: Button, *, action: Callable[[Any], Coroutine[None, None, RequestAction]] = None):
        if button.style == ButtonStyle.URL:
            raise DynamicRequestTypeError('Non-URL Button')

        super(DynamicButton, self).__init__(style=button.style, label=button.label, emoji=button.emoji, custom_id=button.custom_id, disabled=button.disabled)

        self.button = button
        if action is not None:
            self.action = action

    @property
    def id(self):
        return self.button.custom_id

    async def action(self, event: ComponentContext) -> RequestAction:
        raise NotImplementedError


class DynamicButtonRequest(DynamicRequest, ABC):
    def __init__(self, ctx: Union[Context, SlashContext], target: User, *buttons: DynamicButton):
        super().__init__(RequestEvent.Component, ctx, target)
        self.buttons = list(buttons)

    async def handle_unwanted_request(self, ctx: ComponentContext):
        raise NotImplementedError

    def check(self, ctx: ComponentContext):
        if ctx.origin_message_id != self.request_message.id:
            return False
        if ctx.author != self.target:
            ensure_future(self.handle_unwanted_request(ctx))
            return False
        return True

    async def handle_event(self, event: ComponentContext) -> RequestAction:
        for button in self.buttons:
            if button.custom_id == event.custom_id:
                return await button.action(event)

        return RequestAction.Repeat
