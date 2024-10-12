import os

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils import CacheDict, path_exists
from config import BASE_DIR


class ImageCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.cache = CacheDict()

    async def dispatch(self, request: Request, call_next):
        # Проверяем, запрашивается ли изображение
        if request.url.path.startswith('/media/avatars/'):
            filename = request.url.path.split('/')[-1]
            if filename in self.cache:
                return self.cache[filename]
            else:
                path = BASE_DIR.joinpath(f'media/avatars/').joinpath(filename)

                if not await path_exists(path):
                    return Response(status_code=404)

                with open(path, 'rb') as file:
                    image_bytes = file.read()

                response = Response(content=image_bytes, media_type="image/png")
                self.cache[filename] = response

                return response
        else:
            return await call_next(request)
