
from redis import Redis
import time
import json

# these are all actions that can be taken
class NotImplementedException(Exception): pass

# all the parsed inputs should inherit from this
class BaseInput(object):
    def evaluate(self):
        raise NotImplementedException()
# levels
class CreateLevel(BaseInput):
    def __init__(self, name, points):
        self.name, self.points = name, points

    def evaluate(self):
        r = get_redis()
        r.hset('levels', self.name, self.points)
        return {"result":"ok"}

class GetLevels(BaseInput):
    def evaluate(self):
        return {"levels":[]}


# end levels

class Stats(BaseInput):
    def __init__(self, user):
        self.user = user
    def evaluate(self):
        r = get_redis()
        key = 'user_points:' + self.user

        try:
            points = int(r.get(key))
        except:
            points = 0

        key = 'user_badges:' + self.user
        badges = r.hgetall(key)

        result = {}
        for i in badges:
            result[i] = int(badges[i])


        return {"points":points, "badges":result}


# this the raw points award
# award 5 points to user 10
class RawAward(BaseInput):
    def get_dict_to_save(self):
        raise NotImplementedException()

    def post_evaluate(self):
        pass

    def evaluate(self):
        k = 'user_history:' + self.user
        tmp = self.get_dict_to_save()
        tmp['time'] = int(time.time())
        if self.eventid:
            tmp['eventid'] = self.eventid
        tmp = json.dumps(tmp)
        r = get_redis()
        r.lpush(k, tmp)
        result = self.post_evaluate()
        return result



class PointsAward(RawAward):
    def __init__(self, user, points, eventid = None):
        self.user = user
        self.points = int(points)
        self.eventid = eventid
    def get_dict_to_save(self):
        return dict(points = self.points)
    def post_evaluate(self):
        # update the users total points
        r = get_redis()
        k = 'user_points:' + self.user
        result = r.incr(k, self.points)
        # update the global leaderboard
        r.zadd('leaderboard', self.user, result)
        return dict(points=result)

class BadgeAward(RawAward):
    def __init__(self, user, badge, eventid = None):
        self.user = str(user)
        self.badge = str(badge)
        self.eventid = eventid

    def get_dict_to_save(self):
        return dict(badge=self.badge)

    def post_evaluate(self):
        r = get_redis()
        k = 'user_badges:' + self.user
        r.hincrby(k, self.badge, 1)

class EventHistory(BaseInput):
    def __init__(self, user, page = 1, perpage=50):
        self.user, page, perpage = user, page, perpage
    def evaluate(self):
        return {}

class AwardHistory(BaseInput):
    def __init__(self, user, page = 1, perpage=50):
        self.user, page, perpage = user,page, perpage
    def evaluate(self):
        r = get_redis()
        return {}

def get_redis():
    return Redis()
