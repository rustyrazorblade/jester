
from tornado.testing import LogTrapTestCase
from jester.parser import Parser, RuleList

class AddTest(LogTrapTestCase):
    def setUp(self):
        self.r = Parser.parse('create rule test on game_play award 5 points')

    def test_add(self):
        RuleList.add( self.r )

    def test_load_rules(self):
        RuleList.load_rules()


