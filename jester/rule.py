
class RuleDoesNotExistException(Exception): pass

class RuleList(object):
    rules = {}
    
    @classmethod
    def add(cls, rule):
        name = rule.name
        cls.rules[name] = rule

    @classmethod
    def save_rules(cls):
        pass

    @classmethod
    def load_rules(cls):
        pass
    
    @classmethod
    def delete_rule(cls, rule):
        try:
            del cls.rules[rule]
        except:
            raise RuleDoesNotExistException




class Rule(object):

    def __init__(self, event, min_occurences, timeframe):
        self._event = event
        self._min_occurences
        self._timeframe = timeframe
    
    def evaluate(self):
        pass




