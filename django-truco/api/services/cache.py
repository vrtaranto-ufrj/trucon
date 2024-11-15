from django.core.cache import cache
from typing import Callable, Generic, TypeVar 

T = TypeVar('T')

class CacheService(Generic[T]):
    @staticmethod
    def get_cache(
        key: str,
        function_request: Callable[[],T],
        timeout: int = 60 * 15,
    ) -> T:
        
        data: T = cache.get(key)

        if not data:
            data = function_request()
            cache.set(key, data, timeout)

        return data
