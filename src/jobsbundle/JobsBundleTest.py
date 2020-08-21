import unittest
from injecta.testing.servicesTester import testServices
from jobsbundle.containerInit import initContainer

class JobsBundleTest(unittest.TestCase):

    def setUp(self) -> None:
        self.__container = initContainer('test')

    def test_init(self):
        testServices(self.__container)

if __name__ == '__main__':
    unittest.main()
