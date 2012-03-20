
from tornado.testing import LogTrapTestCase
from jester.levels import Levels

class LevelsTest(LogTrapTestCase):
    def test_create(self):

        Levels.flush()
        Levels.create('start', 0)
        
        tmp = Levels.get_level_by_points(5)

        assert tmp == 'start'


        Levels.create('second', 10)
        Levels.create('third', 20)
        Levels.create('four', 30)
        assert len(Levels.levels) == 4
        
        tmp = Levels.get_level_by_points(15)
        assert tmp  == 'second'
        
        tmp = Levels.get_level_by_points(20)
        assert tmp  == 'third'

        tmp = Levels.get_level_by_points(30)
        assert tmp  == 'four'

        tmp = Levels.get_level_by_points(0)
        assert tmp  == 'start'

        tmp = Levels.get_level_by_points(-1)
        assert tmp  == None

        levels = Levels.get_levels()
        assert len(levels) == 4

    
