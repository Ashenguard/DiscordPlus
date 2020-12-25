import re
import sys
import traceback
from typing import Union


def format_exception(exception: Exception) -> str:
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
    return "".join(exception_list)[:-1]


def extract_number(text, required_pattern='\d+', cast_float: bool = False) -> Union[int, float]:
    if text is None:
        return 0
    try:
        cast = float if cast_float else int
        match = re.findall(required_pattern, text)[0]
        number = re.findall('\d+', match)[0]
        return cast(number)
    except Exception:
        return 0


def print_traceback(exception, *, message='Execute failed'):
    print(f'{message} due {exception.__class__.__name__}:')
    print(format_exception(exception))
