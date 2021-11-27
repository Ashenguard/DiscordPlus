import json
import os
from typing import Callable, Any

import yaml


class DatabaseEncoder:
    def encode(self, data: dict) -> str:
        raise NotImplementedError()

    def decode(self, data: str) -> dict:
        raise NotImplementedError()

    JSON: 'DatabaseEncoder' = None
    YAML: 'DatabaseEncoder' = None


class __JSONEncoder(DatabaseEncoder):
    def encode(self, data: dict) -> str:
        return json.dumps(data, indent=2)

    def decode(self, data: str) -> dict:
        return json.loads(data)


class __YAMLEncoder(DatabaseEncoder):
    def encode(self, data: dict) -> str:
        return yaml.safe_dump(data)

    def decode(self, data: str) -> dict:
        return yaml.safe_load(data)


DatabaseEncoder.JSON = __JSONEncoder()
DatabaseEncoder.YAML = __YAMLEncoder()


class DatabaseProperty:
    def __init__(self, name, path=None, cast=None, get_wrapper: Callable[['Database', Any], Any] = None, set_validator: Callable[['Database', Any], bool] = None):
        if path is None:
            path = name

        self.name = name
        self.path = path
        self.cast = cast
        self.get_wrapper = get_wrapper
        self.set_validator = set_validator

    def fget(self, database: 'Database'):
        if self.get_wrapper:
            return self.get_wrapper(database, database.get_data(self.path, self.cast))
        else:
            return database.get_data(self.path, self.cast)

    def fset(self, database: 'Database', value):
        if self.set_validator is None or self.set_validator(database, value):
            database.set_data(self.path, value)
        else:
            raise ValueError(f"value '{value}' is not acceptable by '{self.name}'")


class Database:
    def __init__(self, file_path: str, encoder: DatabaseEncoder, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        self._file_path = file_path
        self._encoding = encoding
        self._encoder = encoder

        if not os.path.exists(self._file_path):
            if create_if_missing:
                os.makedirs(self._file_path[:self._file_path.rfind('/')], exist_ok=True)
                self.save_data(default_data or {})
            else:
                raise FileNotFoundError(f'"{self._file_path}" does not exists')

    def save_data(self, data: dict):
        with open(file=self._file_path, mode='w', encoding=self._encoding) as file:
            file.write(self._encoder.encode(data))

    def load_data(self) -> dict:
        with open(file=self._file_path, mode='r', encoding=self._encoding) as file:
            return self._encoder.decode(file.read())

    def get_data(self, path: str = None, cast: type = None):
        data = self.load_data().copy()
        if path is None:
            return data

        pattern = path.split('.')
        for key in pattern:
            if isinstance(data, dict):
                if key in data.keys():
                    data = data[key]
                else:
                    return None
            elif isinstance(data, list):
                try:
                    data = data[int(key)]
                except Exception:
                    return None
            else:
                return None

        return data if cast is None or data is None else cast(data)

    def set_data(self, path: str, value, default: bool = False):
        original = self.load_data().copy()
        data = original

        pattern = path.split('.')

        for key in pattern[:-1]:
            if key in data.keys():
                data = data[key]
            else:
                data[key] = {}
                data = data[key]

        if default is False or pattern[-1] not in data.keys():
            data[pattern[-1]] = value

        self.save_data(original)

    def exists(self, path: str) -> bool:
        return self.get_data(path) is not None

    def remove(self, path):
        data = self.load_data()

        pattern = path.split('.')

        target = data
        for key in pattern[:-1]:
            if key in target.keys():
                target = target[key]
            else:
                return False

        if pattern[-1] not in target.keys():
            return False
        target.pop(pattern[-1])
        self.save_data(data)
        return True

    def delete(self, *, confirm: bool):
        if confirm:
            os.remove(self._file_path)

    def add_property(self, name: str, path: str = None, cast=None, default=None, *, get_wrapper: Callable[['Database', Any], Any] = None, set_validator: Callable[['Database', Any], bool] = None):
        setattr(self, name, DatabaseProperty(name, path, cast, get_wrapper, set_validator))
        setattr(self, name, default)

    def __setattr__(self, key, value):
        try:
            v = super(Database, self).__getattribute__(key)
            if isinstance(v, DatabaseProperty):
                v.fset(self, value)
                return
        except Exception:
            pass

        super(Database, self).__setattr__(key, value)

    def __getattribute__(self, item):
        v = super(Database, self).__getattribute__(item)
        if isinstance(v, DatabaseProperty):
            return v.fget(self)
        else:
            return v


class JSONDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super().__init__(file_path, DatabaseEncoder.JSON, create_if_missing, default_data, encoding)


class YAMLDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super().__init__(file_path, DatabaseEncoder.YAML, create_if_missing, default_data, encoding)
