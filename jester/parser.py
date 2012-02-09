
from redis import Redis
from logging import info
import logging
import json
import time

from pyparsing import Word, alphas, nums, alphanums, \
        Keyword, LineEnd, Optional, oneOf, LineStart

logging.basicConfig(level=logging.INFO)

class ParseException(Exception): pass


# these are all actions that can be taken
class NotImplementedException(Exception): pass

# all the parsed inputs should inherit from this
class BaseInput(object):
    def evaluate(self):
        raise NotImplementedException()

class ShowRules(BaseInput): 
    def evaluate(self):
        result = {}
        for r in RuleList.rules:
            result[r] = RuleList.rules[r].rule.strip()

        return result

class DeleteRule(BaseInput):
    def __init__(self, rule_name):
        self.rule_name = rule_name
    def evaluate(self):
        RuleList.delete_rule(self.rule_name)
        return {'result':'deleted'}

class FlushDB(BaseInput):
    def evaluate(self):
        r = get_redis()
        r.flushdb()
        RuleList.rules = {}
        return {'flushed':'ok'}

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

class Event(BaseInput):
    def __init__(self, user, event):
        self.user = user
        self.event = event
        self.event_stream = 'event_stream:{0}:{1}'.format(user, event)
        self.awards = []

    def evaluate(self):
        '''
        look at each rule
        if it applies to the event
            if x > 1:
                slice the event stream at x-1 
            else 
                give award
        store a {timestamp, [awards]}

        '''
        for (name,r) in RuleList.rules.iteritems():
            if self.check(r) is True:
                info("Rule match: {0} on event {1}".format(name, self.event))
                tmp = r.apply(self.user)
                self.awards.append(tmp)

        self.save_to_stream()
        
        return {'awards': self.awards }

    # is a rule
    def check(self, r):
        assert isinstance(r, Rule) 

        if r.event != self.event:
            info("rule {0} doesn't apply".format(r.name))
            return False

        # use case covers when something should always be triggered
        if r.min_occurences == 1:
            return True

        redis = get_redis()
        
        # we pull 1 less than the min because we haven't pushed this event into the stream yet
        rows = redis.lrange(self.event_stream, 0, r.min_occurences - 1)
        now = int(time.time())
        min_acceptable_time = now - r.time
        if len(rows) < r.min_occurences - 1:
            info("Failed to meet min_occurances of {0}".format(r.min_occurances))
            return False
        for tmp in rows:
            i = json.loads(tmp)
            if i['time'] < min_acceptable_time:
                return False
        
        return True

    def save_to_stream(self):
        r = get_redis()
        data = {"time":int(time.time())}
        data['awards'] = self.awards
        data = json.dumps(data)
        r.lpush(self.event_stream,data)

class EventHistory(BaseInput):
    def __init__(self, user, page = 1, perpage=50):
        self.user, page, perpage = user, page, perpage
    def evaluate(self):
        return {}

class AwardHistory(BaseInput):
    def __init__(self, user, page = 1, perpage=50):
        self.user, page, perpage = user,page, perpage
    def evaluate(self):
        return {}

        
        
class Parser(object):

    # keywords
    points = Keyword('points', caseless=True)
    badge = Keyword('badge', caseless=True)
    on_ = Keyword('on', caseless=True)
    award = Keyword('award', caseless=True)
    in_ = Keyword('in', caseless=True)
    to = Keyword('to', caseless=True)
    userid = Word(alphanums + "-_")
    show = Keyword('show', caseless=True)
    rules = Keyword('rules', caseless=True)
    rule = Keyword('rule', caseless=True)
    delete = Keyword('delete', caseless=True)
    create = Keyword('create', caseless=True)
    rule_name = Word(alphanums + "_-")
    event_name = Word(alphanums + "_-")
    eval_ = Keyword('eval', caseless=True)
    for_ = Keyword('for', caseless=True)
    history = Keyword('history', caseless=True)
    event = Keyword('event', caseless=True)
    flushdb = Keyword('flushdb', caseless=True)

    create_rule = (create + rule).setResultsName('create_rule')
    create_rule_name = create_rule + rule_name('rule_name')

    delete_rule = (delete + rule).setResultsName('delete_rule') + rule_name('rule_name')

    # keywords - predicates
    when = Keyword('when', caseless=True)
    occurs = Keyword('occurs', caseless=True)
    times = oneOf('times time', caseless=True)
    timeframe = oneOf("minute minutes hour hours day days week weeks month months year years", caseless=True)

    # award 
    award_points = Word(nums)('points') + points.suppress()
    award_badge = badge + Word(alphas + "-_")('badge')
    points_or_badge = award_points ^ award_badge
    award_name = Word(alphanums + "-_")

    #predicates
    predicate = when.suppress() + event_name('predicate_event') + \
                occurs + Word(nums)('min_occurances') + \
                times + in_ + Word(nums)('timeframe_num') + \
                timeframe('timeframe')

    on_event = on_ + event_name.setResultsName('on_event') 

    rule = create_rule_name +  on_event + award + points_or_badge \
                + Optional(predicate)
    # raw award
    raw_award = award('raw_award') + points_or_badge + to.suppress() + userid('userid')

    # shw rules
    show_rules = (show + rules).setResultsName('show_rules')
    
    # push event in: eval <event name> for <user>
    # example: eval game_play for jhaddad
    eval_query = eval_('eval') + event_name('event_name') + for_ + userid('userid')
    
    # award history for jhaddad
    award_history = (award + history)('award_history') + for_ + userid('userid')
    event_history = (event + history)('event_history') + for_ + userid('userid')

    ## final
    command = LineStart() + \
              (eval_query | rule | raw_award | award_history | event_history | show_rules | delete_rule | flushdb('flushdb') ) + \
              LineEnd()

    @classmethod
    def parse(cls, s):
        """docstring for parse"""
        tmp = cls.command.parseString(s).asDict()
        if "delete_rule" in tmp:
            return DeleteRule(tmp['rule_name'])
        if "show_rules" in tmp:
            return ShowRules()
        if "raw_award" in tmp and "points" in tmp:
            return PointsAward( tmp['userid'], tmp['points'] )
        if "raw_award" in tmp and "badge" in tmp:
            return BadgeAward( tmp['userid'], tmp['badge'] )
        if "create_rule" in tmp:
            name = tmp.get('rule_name')
            event = tmp['on_event']
            timeframe = tmp.get('timeframe')
            timeframe_num = tmp.get('timeframe_num',0)
            min_occurances = tmp.get('min_occurances', 1)
            time = cls.convert_time_to_seconds( timeframe_num, timeframe )

            if 'badge' in tmp:
                return BadgeRule(s, name, event, min_occurances, time, tmp['badge'])
            elif 'points' in tmp:
                return PointsRule(s, name, event, min_occurances, time, tmp['points'])
        if "eval" in tmp:
            return Event(tmp['userid'], tmp['event_name'])

        if "award_history" in tmp:
            return AwardHistory(tmp['userid'])
        if "event_history" in tmp:
            return AwardHistory(tmp['userid'])
        if tmp == {'flushdb': 'flushdb'}:
            return FlushDB()

        raise ParseException(s)

    @classmethod
    def convert_time_to_seconds(cls, num, timeframe):
        try:
            num = int(num)
            if timeframe[-1] == 's':
                timeframe = timeframe[:-1]
            src = { 'second': 1 }
            src['minute'] = src['second'] * 60
            src['hour'] = src['minute'] * 60
            src['day'] = src['hour'] * 24
            src['week'] = src['day'] * 7
            src['year'] = src['day'] * 365
            
            return num * src[timeframe]

        except:
            return 0

class RuleDoesNotExistException(Exception): pass

class RuleList(object):
    rules = {}
    redis = Redis()
    rules_key = 'active_rules'
    rule_prefix = "rule:"

    @classmethod
    def add(cls, rule):
        name = rule.name
        cls.rules[name] = rule

        # save to redis
        rkey = cls.rule_prefix + name
        cls.redis.sadd(cls.rules_key, rkey)  
        cls.redis.set( rkey, rule.rule )

    @classmethod
    def load_rules(cls):
        rules = cls.redis.smembers(cls.rules_key)
        for r in rules:
            tmp = cls.redis.get(r)
            info("loading rule {0} from redis: {1}".format(r, tmp))
            rule = Parser.parse(tmp)
            name = rule.name
            cls.rules[name] = rule
    
    @classmethod
    def delete_rule(cls, rule):
        try:
            del cls.rules[rule]
            cls.redis.srem(cls.rules_key, cls.rule_prefix + rule)
        except:
            raise RuleDoesNotExistException(rule)


class Rule(object):
    def __init__(self, rule, name, event, min_occurences = 0, time = 0):
        '''
        rule -> original string rule that came in
        min_occurences -> when event occurs <min_occurences> times in <time>
        '''
        self.rule = rule
        self.name = name
        self.event = event
        self.min_occurences = int(min_occurences)
        self.time = time

    def evaluate(self):
        RuleList.add(self)
        return {'result':'ok'}
    def apply(self, user):
        raise NotImplementedException()

class PointsRule(Rule):
    """docstring for CreatePointsRule"""
    def __init__(self, rule, name, event, min_occurences, time, points):
        super(PointsRule, self).__init__(rule, name, event, min_occurences, time)
        self.points = points
    def apply(self, user):
        tmp = PointsAward(user, self.points)
        return {'points':tmp.points}

class BadgeRule(Rule):
    """docstring for CreateBadgeRule"""
    def __init__(self, rule, name, event, min_occurences, time, badge):
        super(BadgeRule, self).__init__(rule, name, event, min_occurences, time, )
        self.badge = badge
    def apply(self,user):
        tmp = BadgeAward(user, self.badge)
        return {'badge':tmp.badge}


def get_redis():
    return Redis()
