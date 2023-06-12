import os
import json
from typing import Generator


class Cache:
    """
    Cache utility.
    """

    PATH: str = os.path.join(os.sep, "tmp")

    def __init__(self, key: str):
        """
        Cache constructor.
        """
        self.key: str = key
        if not os.path.isdir(self.PATH):
            raise OSError('Not found:', self.PATH)

    @property
    def path(self) -> str:
        """
        Path getter.
        """
        return os.path.join(self.PATH, self.key)

    def exists(self) -> bool:
        """
        Evaluates if a key is cached in the filesystem.
        """
        return os.path.isfile(self.path)

    def save(self, data: dict):
        """
        Saves some data into a cache file.
        """
        with open(self.path, "w", encoding='utf-8') as file_handler:
            json.dump(data, file_handler, ensure_ascii=False, indent=4, sort_keys=True)

    def load(self) -> dict:
        """
        Reads a single cached file.
        """
        with open(self.path, "r", encoding='utf-8') as file_handler:
            return json.load(file_handler)

    @classmethod
    def all(cls) -> Generator['Cache', None, None]:
        """
        Lists all cached files.
        """
        for key in os.listdir(cls.PATH):
            print('Cache:', key)
            if os.path.isfile(os.path.join(cls.PATH, key)):
                yield cls(key)
