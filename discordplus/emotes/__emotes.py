import yaml


class __Emotes:
    def __init__(self, category):
        self.category = category

    def get(self, item, default=None):
        return self.__getitem__(item) or default

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError(f'Only accepts "str" but "{type(item)}" was given.')
        import pkgutil

        data = pkgutil.get_data(__name__, f'{self.category}.yml')
        return yaml.safe_load(data).get(item.lower(), None)


People = __Emotes('people')
Nature = __Emotes('nature')
Food = __Emotes('food')
Activities = __Emotes('activities')
Travel = __Emotes('travel')
Objects = __Emotes('objects')
Symbols = __Emotes('symbols')
Flags = __Emotes('flags')


class Emotes:
    grinning = People.get('grinning')
    sunglasses = People.get('sunglasses')
    smiling_imp = People.get('smiling_imp')
    ghost = People.get('ghost')
    robot = People.get('robot')
    thumbsup = People.get('thumbsup')
    thumbsdown = People.get('thumbsdown')
    point_left = People.get('point_left')
    point_right = People.get('point_right')
    point_up = People.get('point_up_2')
    point_down = People.get('point_down')
    speaking_head = People.get('speaking_head')
    bust_in_silhouette = People.get('bust_in_silhouette')
    busts_in_silhouette = People.get('busts_in_silhouette')
    first_place = Activities.get('first_place')
    second_place = Activities.get('second_place')
    third_place = Activities.get('third_place')
    medal = Activities.get('medal')
    military_medal = Activities.get('military_medal')
    trophy = Activities.get('trophy')
    computer = Objects.get('computer')
    keyboard = Objects.get('keyboard')
    desktop = Objects.get('desktop')
    mouse_three_button = Objects.get('mouse_three_button')
    printer = Objects.get('printer')
    coin = Objects.get('coin')
    moneybag = Objects.get('moneybag')
    credit_card = Objects.get('credit_card')
    gem = Objects.get('gem')
    pick = Objects.get('pick')
    axe = Objects.get('axe')
    hammer = Objects.get('hammer')
    gear = Objects.get('gear')
    tada = Objects.get('tada')
    scroll = Objects.get('scroll')
    page_with_curl = Objects.get('page_with_curl')
    page_facing_up = Objects.get('page_facing_up')
    bookmark_tabs = Objects.get('bookmark_tabs')
    round_pushpin = Objects.get('round_pushpin')
    pushpin = Objects.get('pushpin')
    exclamation = Symbols.get('exclamation')
    x = Symbols.get('x')
    white_check_mark = Symbols.get('white_check_mark')
    question = Symbols.get('question')
    negative_squared_cross_mark = Symbols.get('negative_squared_cross_mark')
    trident = Symbols.get('trident')
    fleur_de_lis = Symbols.get('fleur_de_lis')
    beginner = Symbols.get('beginner')
    warning = Symbols.get('warning')
    arrow_right = Symbols.get('arrow_right')
    arrow_left = Symbols.get('arrow_left')
    arrow_up = Symbols.get('arrow_up')
    arrow_down = Symbols.get('arrow_down')
    arrow_upper_right = Symbols.get('arrow_upper_right')
    arrow_lower_right = Symbols.get('arrow_lower_right')
    arrow_lower_left = Symbols.get('arrow_lower_left')
    arrow_upper_left = Symbols.get('arrow_upper_left')
    arrow_forward = Symbols.get('arrow_forward')
    arrow_backward = Symbols.get('arrow_backward')
    arrow_up_small = Symbols.get('arrow_up_small')
    arrow_down_small = Symbols.get('arrow_down_small')
    numbers = (Symbols.get('zero'), Symbols.get('one'), Symbols.get('two'), Symbols.get('three'), Symbols.get('four'), Symbols.get('five'), Symbols.get('six'), Symbols.get('seven'), Symbols.get('eight'), Symbols.get('nine'))
    letters = {c: Symbols.get(f'regional_indicator_{c}') for c in 'abcdefghijklmnopqrstuvwxyz'}
