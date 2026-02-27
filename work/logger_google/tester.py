import unittest


class TestRaceCondition(unittest.TestCase):
    def test(self):
        print(f"Running test for class: {self.__delattr__}")
        pass

class Test(unittest.TestCase):
    """
    TODO: 
        1. race condition with very clear precision
        2. MultiThreading environement
        3. Performance
        4. Flushing of old data
        5. running an existing running process
        6. no process added logic
           
    """
    def testRaceCondition(self):...

    def testMultiThreadedEvn(self):...

unittest.main()
# obj = TestRaceCondition()
# obj.test()