"""
Cache backends to use with tracing enabled.

:copyright: (c) 2016 Pinn Technologies, Inc.
:license: All rights reserved
"""

import pickle  # NOQA
from werkzeug.contrib.cache import (BaseCache, NullCache, SimpleCache, MemcachedCache,  # NOQA
                                    GAEMemcachedCache, RedisCache, FileSystemCache)     # NOQA


def null(app, config, args, kwargs):
    return NullCache()


def simple(app, config, args, kwargs):
    kwargs.update(dict(threshold=config['LOGEX_CACHE_THRESHOLD']))
    return SimpleCache(*args, **kwargs)


def memcached(app, config, args, kwargs):
    args.append(config['LOGEX_CACHE_MEMCACHED_SERVERS'])
    kwargs.update(dict(key_prefix=config['LOGEX_CACHE_KEY_PREFIX']))
    return MemcachedCache(*args, **kwargs)


def gaememcached(app, config, args, kwargs):
    kwargs.update(dict(key_prefix=config['LOGEX_CACHE_KEY_PREFIX']))
    return GAEMemcachedCache(*args, **kwargs)


def filesystem(app, config, args, kwargs):
    args.insert(0, config['LOGEX_CACHE_DIR'])
    kwargs.update(dict(threshold=config['LOGEX_CACHE_THRESHOLD']))
    return FileSystemCache(*args, **kwargs)


def redis(app, config, args, kwargs):
    kwargs.update(dict(
        host=config.get('LOGEX_CACHE_REDIS_HOST', 'localhost'),
        port=config.get('LOGEX_CACHE_REDIS_PORT', 6379),
    ))
    password = config.get('LOGEX_CACHE_REDIS_PASSWORD')
    if password:
        kwargs['password'] = password

    key_prefix = config.get('LOGEX_CACHE_KEY_PREFIX')
    if key_prefix:
        kwargs['key_prefix'] = key_prefix

    db_number = config.get('LOGEX_CACHE_REDIS_DB')
    if db_number:
        kwargs['db'] = db_number

    redis_url = config.get('LOGEX_CACHE_REDIS_URL')
    if redis_url:
        try:
            from redis import redis_from_url
            kwargs['host'] = redis_from_url(
                                redis_url,
                                db=kwargs.pop('db', None),
                            )
        except ImportError:
            pass

    return RedisCache(*args, **kwargs)
