from pathlib import Path
from typing import Union

import aiofiles.os


async def path_exists(path: Union[Path, str]) -> bool:
    try:
        await aiofiles.os.stat(str(path))
    except OSError as e:
        return False
    return True


class CacheDict:
    def __init__(self, max_size=30):
        self.cache = {}
        self.order = []
        self.max_size = max_size

    def __setitem__(self, key, value):
        if key in self.cache:
            # Если ключ уже есть, обновляем значение и перемещаем его в конец
            self.cache[key] = value
            self.order.remove(key)
            self.order.append(key)
        else:
            # Если новый ключ, проверяем размер кэша
            if len(self.cache) >= self.max_size:
                # Удаляем самый старый элемент
                oldest_key = self.order.pop(0)
                del self.cache[oldest_key]
            # Добавляем новый элемент
            self.cache[key] = value
            self.order.append(key)

    def __getitem__(self, key):
        return self.cache[key]

    def __delitem__(self, key):
        del self.cache[key]
        self.order.remove(key)

    def __contains__(self, key):
        return key in self.cache

    def __repr__(self):
        return f"CacheDict({self.cache})"
