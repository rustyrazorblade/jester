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

        tmp = Parser.parse("award 90 points to jhaddad")
        assert type(tmp) is PointsAward

        tmp = Parser.parse("award badge bacon_lover to jhaddad")
        assert type(tmp) is BadgeAward


    def test_show_rules(self):
        Parser.show_rules.parseString('show rules')
        tmp = Parser.parse('show rules')
        assert type(tmp) is ShowRules

    def test_delete_rule(self):
        tmp = Parser.parse('delete rule test_rule')
        assert type(tmp) is DeleteRule

class TimeConverterTest(LogTrapTestCase):
    def test_minutes(self):
        Parser.convert_time_to_seconds('5', 'day')
