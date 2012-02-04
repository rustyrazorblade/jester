
from redis import Redis
from logging import info

from pyparsing import Word, alphas, nums, alphanums, \
        Keyword, LineEnd, Optional, oneOf, LineStart

class ParseException(Exception): pass


# these are all actions that can be taken
class ShowRules(object): pass

class DeleteRule(object):
    def __init__(self, rule_name):
        self.rule_name = rule_name

class PointsAward(object):
    def __init__(self, user, points):
        self.user = user
        self.points = points

class BadgeAward(object):
    def __init__(self, user, badge):
        self.user = user
        self.badge = badge

class Event(object):
    def __init__(self, user, event):
        self.user = user
        self.event = event
        
        
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

    create_rule = (create + rule).setResultsName('create_rule')
    create_rule_name = create_rule + rule_name('rule_name')

    delete_rule = (delete + rule).setResultsName('delete_rule') + rule_name('rule_name')

    # keywords - predicates
    when = Keyword('when', caseless=True)
    occurs = Keyword('occurs', caseless=True)
    times = oneOf('times time', caseless=True)
    timeframe = oneOf("day days week weeks month months year years", caseless=True)

    # award 
    award_points = Word(nums)('points') + points.suppress()
    award_badge = badge + Word(alphas + "-_")('badge')
    points_or_badge = award_points ^ award_badge
    award_name = Word(alphanums + "-_")

    #predicates
    predicate = when.suppress() + award_name('predicate_event') + \
                occurs + Word(nums)('min_occurances') + \
                times + in_ + Word(nums)('timeframe_num') + \
                timeframe('timeframe')

    on_event = on_ + award_name.setResultsName('on_event') 

    rule = create_rule_name +  on_event + award + points_or_badge \
                + Optional(predicate)
    # raw award
    raw_award = award('raw_award') + points_or_badge + to.suppress() + userid('userid')

    # shw rules
    show_rules = (show + rules).setResultsName('show_rules')

    ## final
    command = LineStart() + \
              (rule | raw_award | show_rules | delete_rule ) + \
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
            min_occurances = tmp.get('min_occurances', 0)
            time = cls.convert_time_to_seconds( timeframe_num, timeframe )

            if 'badge' in tmp:
                return BadgeRule(s, name, event, min_occurances, time, tmp['badge'])
            elif 'points' in tmp:
                return PointsRule(s, name, event, min_occurances, time, tmp['points'])
            
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
        self.min_occurences = min_occurences
        self.time = time

class PointsRule(Rule):
    """docstring for CreatePointsRule"""
    def __init__(self, rule, name, event, min_occurences, time, points):
        super(PointsRule, self).__init__(rule, name, event, min_occurences, time)
        self.points = points

class BadgeRule(Rule):
    """docstring for CreateBadgeRule"""
    def __init__(self, rule, name, event, min_occurences, time, badge):
        super(BadgeRule, self).__init__(rule, name, event, min_occurences, time, )
        self.badge = badge



