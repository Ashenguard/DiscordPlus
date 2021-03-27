from datetime import timedelta, datetime

from discord.ext import tasks

from .lib import ExceptionFormat, async_wrapper


def _reformat_time(s, m, h):
    m += (h - int(h)) * 60
    h = int(h)
    s += (m - int(m)) * 60
    m = int(m)
    s = int(s)

    new_s = s % 60
    new_m = (m + s // 60) % 60
    h += (m + s // 60) // 60
    return new_s, new_m, h


class TaskPlusStatus:
    def __init__(self, **kwargs):
        self.goal = kwargs.get('goal', timedelta())
        self.average = kwargs.get('average', timedelta())
        self.running = kwargs.get('running', False)
        self.accuracy = kwargs.get('accuracy', 0)
        self.last = kwargs.get('last', datetime.fromtimestamp(0))
        self.next = kwargs.get('next', self.last + self.goal)
        self.duration = kwargs.get('duration', timedelta())
        

class TaskPlus:
    __tasks = []

    class __Runner:
        def __init__(self, func, checks=None):
            if checks is None:
                checks = []

            self.task = None
            self.func = func
            self.conditions = checks

        async def run(self):
            for condition in self.conditions:
                if not condition(self.task):
                    return

            await self.func(self.task)

    @staticmethod
    def execute(func):
        try:
            checks = func.__func_checks__
        except AttributeError:
            checks = []

        return TaskPlus.__Runner(async_wrapper(func), checks)

    @staticmethod
    def check(*conditions):
        def decorator(func):
            wrapped_conditions = [async_wrapper(condition) for condition in conditions]

            if isinstance(func, TaskPlus.__Runner):
                func.conditions.extend(wrapped_conditions)
            else:
                if not hasattr(func, '__func_checks__'):
                    func.__func_checks__ = []
                func.__func_checks__.extend(conditions)
            return func
        return decorator

    def __init__(self, bot, *, seconds=0, minutes=1, hours=0):
        seconds, minutes, hours = _reformat_time(seconds, minutes, hours)

        self.goal = timedelta(seconds=seconds, minutes=minutes, hours=hours)
        self.average_duration = timedelta()
        self.last_run = datetime.now() - self.goal
        self.average_run = timedelta()
        self.runs = 0
        self.bot = bot
        self.set_interval(seconds=seconds, minutes=minutes, hours=hours)

        for value in self.__class__.__dict__.values():
            if value.__class__ == TaskPlus.__Runner:
                self.__tasks.append(value)
                value.task = self

    def calculate_accuracy(self):
        self.average_run = (self.average_run * self.runs + (datetime.now() - self.last_run)) / (self.runs + 1)
        self.last_run = datetime.now()

    def calculate_duration(self):
        self.average_duration = (self.average_duration * self.runs + (datetime.now() - self.last_run)) / (self.runs + 1)
        self.runs += 1

    def set_interval(self, *, seconds=0, minutes=1, hours=0):
        self.loop.change_interval(seconds=seconds, minutes=minutes, hours=hours)
        self.goal = timedelta(seconds=seconds, minutes=minutes, hours=hours)

    def start(self):
        self.loop.start()

    def stop(self):
        self.loop.stop()

    @tasks.loop(minutes=1)
    async def loop(self):
        self.calculate_accuracy()
        for runner in TaskPlus.__tasks:
            try:
                await runner.run()
            except Exception as error:
                ExceptionFormat(error).print(message=f'Unable to run "{runner}"')

        self.calculate_duration()

    @loop.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()

    @property
    def status(self) -> TaskPlusStatus:
        return TaskPlusStatus(
            goal=self.goal,
            average=self.average_run,
            running=self.loop.is_running(),
            accuracy=round(100 - 100 * max(self.average_run - self.goal, timedelta()) / self.goal, 2),
            last=self.last_run,
            next=self.last_run + self.goal,
            duration=self.average_duration
        )
