

from pyparsing import Word, alphas, nums, alphanums, \
        Keyword, LineEnd, Optional, oneOf, LineStart

class Parser(object):

    # keywords
    points = Keyword('points', caseless=True)
    badge = Keyword('badge', caseless=True)
    on_ = Keyword('on', caseless=True)
    award = Keyword('award', caseless=True)
    in_ = Keyword('in', caseless=True)
    to = Keyword('to', caseless=True)
    userid = Word(alphanums + "-_")

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

    rule = on_event + award + points_or_badge \
                + Optional(predicate)
    # raw award
    raw_award = award + points_or_badge + to.suppress() + userid('userid')
    ## final
    command = LineStart() + \
              (rule ^ raw_award) + \
              LineEnd()

    @classmethod
    def parse(cls, s):
        """docstring for parse"""
        tmp = cls.command.parseString(s)
        return tmp







