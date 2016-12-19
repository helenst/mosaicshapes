

import unittest
from grid import Grid


class TestGrid(unittest.TestCase):

    def setUp(self):
        self.grid = Grid("./examples/cold_throwback.JPEG", pix=30)
        pass
       
    def tearDown(self):
        pass

    def test_n_pass(self):
        n=1
        self.grid.n_pass(n)

    def test_occupy(self):
        x,y = (10,10)
        self.grid.occupy(x,y)
        result = self.grid.is_occupied(x,y)
        self.assertTrue(result)

    # Test vertical expansion
    def test_is_occupied(self):
        x,y = (10,10)
        result = self.grid.is_occupied(x,y)
        self.assertFalse(result)
        self.grid.occupy(x,y)
        result = self.grid.is_occupied(x,y)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()