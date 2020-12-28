import yaml


class Emotes:
    # Useful emotes
    white_check_mark = '✅'

    # Todo - Add more emotes

    # Methods
    def __init__(self, category):
        self.category = category

    def get(self, item, default=None):
        return self.__getitem__(item) or default

    def __getitem__(self, item):
        with open(f'./{self.category}.yml', 'r') as file:
            data = yaml.load(file.read())

        return data.get(item, None)


People = Emotes('people')
Nature = Emotes('nature')
Food = Emotes('food')
Activities = Emotes('activities')
People = Emotes('travel')
People = Emotes('objects')
People = Emotes('symbols')
People = Emotes('flags')
