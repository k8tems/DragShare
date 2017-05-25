import unittest
import main


class TestGetAreaSrc(unittest.TestCase):
    def setUp(self):
        self.area = main.Area()

    def test_press_x_y_less_than_release_x_y(self):
        self.area['press'] = 10, 10
        self.area['release'] = 20, 20
        self.assertEqual((10, 10), self.area.src)
        self.assertEqual((20, 20), self.area.dest)

    def test_press_y_greater_than_release_y(self):
        self.area['press'] = 10, 30
        self.area['release'] = 20, 20
        self.assertEqual((10, 20), self.area.src)
        self.assertEqual((20, 30), self.area.dest)

    def test_press_y_y_greater_than_release_y(self):
        self.area['press'] = 20, 20
        self.area['release'] = 10, 10
        self.assertEqual((10, 10), self.area.src)
        self.assertEqual((20, 20), self.area.dest)


if __name__ == '__main__':
    unittest.main()
