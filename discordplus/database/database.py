import json
import os
import yaml


class DatabaseLanguage:
    def encode(self, data: dict) -> str:
        raise NotImplementedError()

    def decode(self, data: str) -> dict:
        raise NotImplementedError()

    JSON = None
    YAML = None


class __JSONLanguage(DatabaseLanguage):
    def encode(self, data: dict) -> str:
        return json.dumps(data, indent=2)

    def decode(self, data: str) -> dict:
        return json.loads(data)


class __YAMLLanguage(DatabaseLanguage):
    def encode(self, data: dict) -> str:
        return yaml.safe_dump(data)

    def decode(self, data: str) -> dict:
        return yaml.safe_load(data)


DatabaseLanguage.JSON = __JSONLanguage()
DatabaseLanguage.YAML = __YAMLLanguage()


class Database:
    def __init__(self, file_path: str, language: DatabaseLanguage, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        self.file_path = file_path
        self.encoding = encoding
        self.language = language

        if not os.path.exists(self.file_path):
            if create_if_missing:
                os.makedirs(self.file_path[:self.file_path.rfind('/')], exist_ok=True)
                self.save_data(default_data or {})
            else:
                raise FileNotFoundError(f'"{self.file_path}" does not exists')

    def save_data(self, data: dict):
        with open(file=self.file_path, mode='w', encoding=self.encoding) as file:
            file.write(self.language.encode(data))

    def load_data(self) -> dict:
        with open(file=self.file_path, mode='r', encoding=self.encoding) as file:
            return self.language.decode(file.read())

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
        data = self.load_data().copy()

        pattern = path.split('.')

        for key in pattern[:-1]:
            if key in data.keys():
                data = data[key]
            else:
                data[key] = {}
                data = data[key]

        if pattern[-1] not in data.keys() or default is False:
            data[pattern[-1]] = value

        self.save_data(data)

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
            os.remove(self.file_path)


class JSONDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super().__init__(file_path, DatabaseLanguage.JSON, create_if_missing, default_data, encoding)


class YAMLDatabase(Database):
    def __init__(self, file_path: str, create_if_missing: bool = True, default_data=None, encoding='utf8'):
        super().__init__(file_path, DatabaseLanguage.YAML, create_if_missing, default_data, encoding)
