
from redis import Redis

r = Redis()
def get_redis():
    return r 

class Levels(object):
    levels = {}
    redis = get_redis()
    
    def __init__(self, redis):
        pass

    @classmethod
    def create(cls, name, points):
        """docstring for create"""
        cls.levels[name] = points
        cls.redis.hset('levels', name, points)
        

    @classmethod
    def get_level_by_points(cls, points):
        current = None

        for k,v in cls.levels.iteritems():
            if current is None and points >= v:
                current = k
                continue
            if points >= v and v >= cls.levels[current]:
                current = k

        return current

    @classmethod
    def load(cls):
        r = cls.redis
        cls.levels = r.hgetall('levels')

    @classmethod
    def flush(cls):
        cls.redis.delete('levels')

    @classmethod
    def get_levels(cls):
        return cls.levels

        


