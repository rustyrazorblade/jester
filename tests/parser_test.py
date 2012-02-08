import ipdb

from logging import info
from tornado.testing import LogTrapTestCase
from jester.parser import *

class ParserTest(LogTrapTestCase):

    def test_create_rule_partial(self):
        tmp = Parser.create_rule.parseString('create rule')
        info(tmp)

    def test_rules(self):
        t = ['create rule blah on game_play award 5 points',
             'create rule blah2 on gold_miner award badge gold_miner_pro',
             'create rule blah3 on eat_bacon award badge fatass']

        for s in t:
            info( "parsing " + s )
            tree = Parser.parse( s )
            info(  tree )
            #print tree

    def test_partial_predicates(self):
        s = "when play occurs 3 times in 1 day"
        result = Parser.predicate.parseString(s)

    def test_predicates(self):
        t = ['create rule big_player on game_play award badge big_player when game_play occurs 3 times in 1 day',
             'create rule game_play_points on game_play award 6 points  when game_play occurs 3 times in 1 day',
             'create rule kick_friend_face on kick_friend_in_face award badge face_kicker when kick_friend_in_face occurs 10 times in 1 year']
        for s in t:
            tree = Parser.parse( s )
            #print tree.asDict()

    def test_raw_award(self):
        tmp = Parser.parse("award 90 points to 105")
        assert type(tmp) is PointsAward
        assert tmp.points == 90
        assert tmp.user == "105"
        tmp.evaluate()

        tmp = Parser.parse("award 90 points to jhaddad")
        assert type(tmp) is PointsAward
        tmp.evaluate()

        tmp = Parser.parse("award badge bacon_lover to jhaddad")
        assert type(tmp) is BadgeAward
        tmp.evaluate()


    def test_show_rules(self):
        Parser.show_rules.parseString('show rules')
        tmp = Parser.parse('show rules')
        assert type(tmp) is ShowRules

    def test_delete_rule(self):
        tmp = Parser.parse('delete rule test_rule')
        assert type(tmp) is DeleteRule

class TimeConverterTest(LogTrapTestCase):
    def test_minutes(self):
        result = Parser.convert_time_to_seconds('5', 'minutes')
        assert result == 300

    def test_hours(self):
        assert 86400 == Parser.convert_time_to_seconds(1,'day')

class ShowRulesEvaluateTest(LogTrapTestCase):
    def test_show_rules(self):
        result = ShowRules().evaluate()


class CreateRuleEvaluate(LogTrapTestCase):
    def test_evaluate(self):
        s = Parser.parse("create rule blah on game_play award 5 points")
        s.evaluate()

class EvalEventTest(LogTrapTestCase):
    def test_eval(self):
        test_str = "eval game_play for jhaddad"
        Parser.eval_query.parseString(test_str)
        tmp = Parser.parse(test_str)
        tmp.evaluate()

class AwardHistoryTest(LogTrapTestCase):
    def test_award_history(self):
        test_str = "award history for jhaddad"
        Parser.award_history.parseString(test_str)
        Parser.parse(test_str)


class EventHistoryTest(LogTrapTestCase):
    def test_award_history(self):
        test_str = "event history for jhaddad"
        Parser.event_history.parseString(test_str)
        Parser.parse(test_str)
