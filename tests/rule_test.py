
from tornado.testing import LogTrapTestCase
from jester.parser import Parser, RuleList, RuleDoesNotExistException

class AddTest(LogTrapTestCase):
    def setUp(self):
        self.r = Parser.parse('create rule test on game_play award 5 points')

    def test_add(self):
        RuleList.add( self.r )

    def test_load_rules(self):
        RuleList.load_rules()

    def test_delete_rule(self):
        self.r = Parser.parse('create rule test_for_delete on game_play award 5 points')
        RuleList.add( self.r )
        RuleList.delete_rule('test_for_delete')
        RuleList.load_rules()
        with self.assertRaises(RuleDoesNotExistException):
            RuleList.delete_rule('test_for_delete')

