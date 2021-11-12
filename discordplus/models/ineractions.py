from enum import IntEnum
from typing import Union, Optional, List
from uuid import uuid4

from discord import PartialEmoji, Emoji
from discord_slash import ButtonStyle

from discordplus.errors import IncorrectFormatError, IncorrectTypeError


def emoji_to_dict(emoji: Union[Emoji, PartialEmoji, str]) -> dict:
    """
    Converts a default or custom emoji into a partial emoji dict.

    :param emoji: The emoji to convert.
    :type emoji: Union[discord.Emoji, discord.PartialEmoji, str]
    """
    if isinstance(emoji, Emoji):
        return {"name": emoji.name, "id": emoji.id, "animated": emoji.animated}
    elif isinstance(emoji, PartialEmoji):
        return emoji.to_dict()
    elif isinstance(emoji, str):
        return {"name": emoji, "id": None}
    elif isinstance(emoji, dict):
        return emoji
    return {}


class ComponentType(IntEnum):
    InteractionRow = 1
    Button = 2
    Select = 3


class ButtonStyle(IntEnum):
    Blue = 1
    Blurple = 1
    Gray = 2
    Grey = 2
    Green = 3
    Red = 4
    URL = 5

    Primary = 1
    Secondary = 2
    Success = 3
    Danger = 4


class Component:
    def get_data(self) -> dict:
        raise NotImplementedError

    def validate(self) -> None:
        raise NotImplementedError


class Button(Component):
    def __init__(self, style: Union[ButtonStyle, int],
                 label: str = None,
                 emoji: Union[Emoji, PartialEmoji, str] = None,
                 custom_id: str = None,
                 url: str = None,
                 disabled: bool = False):
        self.__init = False
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled
        self.__init = True

        self.validate()

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        if value != ButtonStyle.URL:
            self.url = None
            if self.__init:
                self.custom_id = uuid4()
        else:
            self.custom_id = None

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if self.__init and not self.emoji and not value:
            raise IncorrectFormatError("You can not remove the `labal` when you don't have a `emoji` either.")
        self._label = value

    @property
    def emoji(self):
        return self._emoji

    @emoji.setter
    def emoji(self, value):
        if self.__init and not self.label and not value:
            raise IncorrectFormatError("You can not remove the `emoji` when you don't have a `label` either.")
        self._emoji = emoji_to_dict(value)

    @property
    def custom_id(self):
        return self._custom_id

    @custom_id.setter
    def custom_id(self, value):
        if self._style == ButtonStyle.URL:
            if value:
                raise IncorrectFormatError("You can't have a `custom_id` on a link button!")
            self._custom_id = None
            return
        if not value:
            value = uuid4()
        self._custom_id = str(value)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if self._style != ButtonStyle.URL and value:
            raise IncorrectFormatError("You can't have a `URL` on a non-link button!")
        self._url = value

    @property
    def disabled(self):
        return self._disable

    @disabled.setter
    def disabled(self, value):
        self._disable = True if value else False

    def validate(self) -> None:
        if self.style == ButtonStyle.URL:
            if self.custom_id:
                raise IncorrectFormatError("You can't have a `custom_id` on a link button!")
            if not self.url:
                raise IncorrectFormatError("A link button must have a `url`!")
        elif self.url:
            raise IncorrectFormatError("You can't have a `URL` on a non-link button!")

        if not self.label and not self.emoji:
            raise IncorrectFormatError("You must have at least a `label` or `emoji` on a button.")

    def get_data(self) -> dict:
        self.validate()

        data = {
            "type": ComponentType.Button,
            "style": self.style,
            "label": self.label,
            "emoji": self.emoji,
            "url": self.url,
            "custom_id": self.custom_id,
            "disabled": self.disabled
        }

        for key in list(data.keys()):
            if data[key] is None:
                del data[key]

        return data


class URLButton(Button):
    def __init__(self, label: str = None,
                 emoji: Union[Emoji, PartialEmoji, str] = None,
                 url: str = None,
                 disabled: bool = False):
        super().__init__(ButtonStyle.URL, label, emoji, None, url, disabled)


class PrimaryButton(Button):
    def __init__(self, label: str = None,
                 emoji: Union[Emoji, PartialEmoji, str] = None,
                 custom_id: str = None,
                 disabled: bool = False):
        super().__init__(ButtonStyle.Primary, label, emoji, custom_id, None, disabled)


class SecondaryButton(Button):
    def __init__(self, label: str = None,
                 emoji: Union[Emoji, PartialEmoji, str] = None,
                 custom_id: str = None,
                 disabled: bool = False):
        super().__init__(ButtonStyle.Secondary, label, emoji, custom_id, None, disabled)


class SuccessButton(Button):
    def __init__(self, label: str = None,
                 emoji: Union[Emoji, PartialEmoji, str] = None,
                 custom_id: str = None,
                 disabled: bool = False):
        super().__init__(ButtonStyle.Success, label, emoji, custom_id, None, disabled)


class DangerButton(Button):
    def __init__(self, label: str = None,
                 emoji: Union[Emoji, PartialEmoji, str] = None,
                 custom_id: str = None,
                 disabled: bool = False):
        super().__init__(ButtonStyle.Danger, label, emoji, custom_id, None, disabled)


class SelectOption(Component):
    def __init__(self, label: str, value: str, emoji=None, description: str = None, default: bool = False):
        self.label = label
        self.value = value
        self.emoji = emoji
        self.description = description
        self.default = default

        self.validate()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if not isinstance(value, str):
            value = str(value)
        if not len(value) or len(value) > 100:
            raise IncorrectFormatError("`Label` length should be between 1 and 100.")
        self._label = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, str):
            value = str(value)
        if not len(value) or len(value) > 100:
            raise IncorrectFormatError("`Value` length should be between 1 and 100.")
        self._value = value

    @property
    def emoji(self):
        return self._emoji

    @emoji.setter
    def emoji(self, value):
        self._emoji = emoji_to_dict(value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value or len(value) > 100:
            raise IncorrectFormatError("`Description` length should be between 1 and 100.")
        self._description = value

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = True if value else False

    def validate(self) -> None:
        pass

    def get_data(self) -> dict:
        self.validate()

        return {
            "label": self.label,
            "value": self.value,
            "description": self.description,
            "default": self.default,
            "emoji": self.emoji
        }


class SelectMenu(Component):
    def __init__(self, options: List[SelectOption] = None,
                 custom_id: str = None,
                 placeholder: Optional[str] = None,
                 min_values: Optional[int] = None,
                 max_values: Optional[int] = None,
                 disabled: bool = False):
        self._options = []
        for option in options:
            self.add_option(option)

        self.custom_id = custom_id
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

        self.validate()

    def add_option(self, option: SelectOption):
        self.options.append(option)

    @property
    def options(self):
        return self._options.copy()

    @property
    def custom_id(self):
        return self._custom_id

    @custom_id.setter
    def custom_id(self, value):
        self._custom_id = value if value else uuid4()

    @property
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        self._placeholder = value if value else ""

    @property
    def min_values(self):
        return self._min_values

    @min_values.setter
    def min_values(self, value):
        if not isinstance(value, int):
            raise IncorrectTypeError("Min values must be an integer.")
        self._min_values = value

    @property
    def max_values(self):
        return self._max_values

    @max_values.setter
    def max_values(self, value):
        if not isinstance(value, int):
            raise IncorrectTypeError("Min values must be an integer.")
        self._max_values = value

    @property
    def disable(self):
        return self._disable

    @disable.setter
    def disable(self, value):
        self._disable = True if value else False

    def validate(self) -> None:
        if not len(self.options) or len(self.options) > 25:
            raise IncorrectFormatError("Options length should be between 1 and 25.")

    def get_data(self) -> dict:
        self.validate()

        options = []
        for option in self.options:
            if isinstance(option, SelectOption):
                option = option.get_data()
            options.append(option)

        return {
            "type": ComponentType.Select,
            "options": options,
            "custom_id": self.custom_id,
            "placeholder": self.placeholder,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
        }


class InteractionRow(Component):
    def __init__(self, *components: Component):
        self._components = []
        for component in components:
            self.add_component(component)

    @property
    def components(self):
        return self._components.copy()

    def add_component(self, component: Component):
        if len(self.components) == 5:
            raise IncorrectFormatError("`InteractionRow` can only have 5 compenents")
        if not isinstance(component, Component):
            raise IncorrectTypeError(f"You can only add `Component` to `InteractionRow` not `{type(component)}`")
        if isinstance(component, SelectOption):
            raise IncorrectFormatError("You can't add `SelectOption` to `InteractionRow`")
        if isinstance(component, InteractionRow):
            raise IncorrectFormatError("You can't add another `InteractionRow` to `InteractionRow`")
        if isinstance(component, SelectMenu) and len(self._components) > 1:
            raise IncorrectFormatError("You can't add `SelectMenu` to this `InteractionRow`")

        self._components.append(component)

    def validate(self) -> None:
        if len(self.components) == 0 or len(self.components) > 5:
            raise IncorrectFormatError("InteractionRow can only have 5 compenents")
        for component in self.components:
            if isinstance(component, SelectMenu):
                if len(self.components) > 1:
                    raise IncorrectFormatError("InteractionRow can only support 1 SelectMenu and nothing else")
            if isinstance(component, SelectOption):
                raise IncorrectFormatError("You can't have SelectOption in InteractionRow")
            if isinstance(component, InteractionRow):
                raise IncorrectFormatError("You can't have another InteractionRow in InteractionRow")

    def get_data(self) -> dict:
        self.validate()

        components = [component.get_data() for component in self.components]

        return {
            "type": ComponentType.InteractionRow,
            "components": components
        }


class InteractionMenu(Component):
    def __init__(self, *components: Component):
        self._components: List[InteractionRow] = []
        for component in components:
            self.add_component(component)

    @property
    def components(self):
        return self._components.copy()

    def add_component(self, component: Component):
        if len(self.components) == 5:
            raise IncorrectFormatError("`InteractionRow` can only have 5 compenents")
        if not isinstance(component, Component):
            raise IncorrectTypeError("You can only add `Components` to `InteractionMenu`")
        if isinstance(component, SelectOption):
            raise IncorrectFormatError("You can't add `SelectOption` to `InteractionMenu`")
        if isinstance(component, InteractionMenu):
            raise IncorrectFormatError("You can't add another `InteractionMenu` to `InteractionMenu`")
        if isinstance(component, InteractionRow):
            self._components.append(component)
        if isinstance(component, SelectMenu):
            row = InteractionRow(component)
            self._components.append(row)
        if isinstance(component, Button):
            if len(self._components) > 0:
                try:
                    row = self._components[-1]
                    row.add_component(component)
                    return
                except IncorrectFormatError:
                    row = InteractionRow(component)
                    self._components.append(row)
            else:
                row = InteractionRow(component)
                self._components.append(row)

    def validate(self) -> None:
        if len(self.components) == 0 or len(self.components) > 5:
            raise IncorrectFormatError("`InteractionMenu` can only have 5 compenents")
        for component in self.components:
            if not isinstance(component, InteractionRow):
                raise IncorrectFormatError(f"You can only have `InteractionRow` in `InteractionMenu` not `{type(component)}`")

    def get_data(self) -> List[dict]:
        self.validate()

        return [component.get_data() for component in self.components]


BlueButton = BlurpleButton = PrimaryButton
GrayButton = GreyButton = SecondaryButton
GreenButton = SuccessButton
RedButton = DangerButton
