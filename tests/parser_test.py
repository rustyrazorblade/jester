import ipdb

from tornado.testing import LogTrapTestCase
from jester.parser import Parser

class ParserTest(LogTrapTestCase):

    def test_create_rule_partial(self):
        tmp = Parser.create_rule.parseString('create rule')

    def test_rules(self):
        t = ['create rule blah on game_play award 5 points',
             'create rule blah2 on gold_miner award badge suckit',
             'create rule blah3 on eat_bacon award badge fatass']

        for s in t:
            tree = Parser.parse( s )
            #print tree.asDict()
            #print tree

    def test_partial_predicates(self):
        s = "when play occurs 3 times in 1 day"
        result = Parser.predicate.parseString(s)

    def test_predicates(self):
        t = ['create rule big_player on game_play award badge big_player when game_play occurs 3 times in 1 day',
             'create rule game_play_points on game_play award 6 points  when game_play occurs 3 times in 1 day',
             'create rule kick_tina_face on kick_tina_in_face award badge face_kicker when kick_tina_in_face occurs 10 times in 1 year']
        for s in t:
            tree = Parser.parse( s )

    def test_raw_award(self):
        Parser.parse("award 90 points to 105")
        tree = Parser.parse("award 90 points to jhaddad")
        tree = Parser.parse("award badge bacon_lover to jhaddad")

    def test_show_rules(self):
        return
        Parser.parse('show rules')
