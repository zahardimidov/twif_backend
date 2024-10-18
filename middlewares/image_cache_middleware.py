import os

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils import CacheDict, path_exists
from config import BASE_DIR

cache = CacheDict()

class ImageCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Проверяем, запрашивается ли изображение
        if request.url.path.startswith('/media/'):
            filename = request.url.path.split('/')[-1]
            if filename in cache:
                print('image from cache')
                return cache[filename]
            else:
                if request.url.path.startswith('/media/avatars'):
                    path = BASE_DIR.joinpath(f'media/avatars/').joinpath(filename)
                elif request.url.path.startswith('/media/logos'):
                    path = BASE_DIR.joinpath(f'media/logos/').joinpath(filename)
                elif request.url.path.startswith('/media/message'):
                    path = BASE_DIR.joinpath(f'media/message/').joinpath(filename)

                if not await path_exists(path):
                    return Response(status_code=404)

                with open(path, 'rb') as file:
                    image_bytes = file.read()

                response = Response(content=image_bytes, media_type="image/png")
                cache[filename] = response

                return response
        else:
            return await call_next(request)
