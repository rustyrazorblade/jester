import ipdb

from tornado.testing import LogTrapTestCase
from jester.parser import Parser

class ParserTest(LogTrapTestCase):

    def test_rules(self):
        t = ['on game_play award 5 points',
             'on gold_miner award badge suckit',
             'on eat_bacon award badge fatass']

        for s in t:
            tree = Parser.parse( s )
            #print tree.asDict()
            #print tree

    def test_partial_predicates(self):
        s = "when play occurs 3 times in 1 day"
        Parser.predicate(s)

    def test_predicates(self):
        t = ['on game_play award badge big_player when game_play occurs 3 times in 1 day',
             'on game_play award 6 points  when game_play occurs 3 times in 1 day',
             'on kick_tina_in_face award badge face_kicker when kick_tina_in_face occurs 10 times in 1 year']
        for s in t:
            tree = Parser.parse( s )

    def test_raw_award(self):
        Parser.parse("award 90 points to 105")
        tree = Parser.parse("award 90 points to jhaddad")
        tree = Parser.parse("award badge bacon_lover to jhaddad")
