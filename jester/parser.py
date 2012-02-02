

from pyparsing import Word, alphas, nums, alphanums, \
        Keyword, LineEnd, Optional, oneOf, LineStart, \
        Combine

class ShowRules(object): pass

class DeleteRule(object):
    def __init__(self, rule_name):
        self.rule_name = rule_name


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
    create_rule_name = create_rule + rule_name

    delete_rule = (delete + rule).setResultsName('delete_rule') + rule_name

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
    raw_award = award + points_or_badge + to.suppress() + userid('userid')

    # shw rules
    show_rules = (show + rules).setResultsName('show_rules')

    ## final
    command = LineStart() + \
              (rule | raw_award | show_rules | delete_rule ) + \
              LineEnd()

    @classmethod
    def parse(cls, s):
        """docstring for parse"""
        tmp = cls.command.parseString(s)
        return tmp

    @classmethod
    def convert_time_to_seconds(cls, num, timeframe):
        if timeframe[-1] == 's':
            timeframe = timeframe[:-1]
        
        src = { 'second': 1 }
        src['minute'] = src['second'] * 60
        src['hour'] = src['minute'] * 60
        src['day'] = src['hour'] * 24
        src['week'] = src['day'] * 7








