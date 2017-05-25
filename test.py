import unittest
import main


class TestGetArea(unittest.TestCase):
    def setUp(self):
        self.area = main.Area()

    def test_press_x_y_less_than_release_x_y(self):
        self.area['press'] = 10, 10
        self.area['release'] = 20, 20
        self.assertEqual((10, 10, 20, 20), self.area.bbox)

    def test_press_y_greater_than_release_y(self):
        self.area['press'] = 10, 30
        self.area['release'] = 20, 20
        self.assertEqual((10, 20, 20, 30), self.area.bbox)

    def test_press_x_greater_than_release_x(self):
        self.area['press'] = 30, 10
        self.area['release'] = 20, 20
        self.assertEqual((20, 10, 30, 20), self.area.bbox)

    def test_press_x_y_greater_than_release_y(self):
        self.area['press'] = 20, 20
        self.area['release'] = 10, 10
        self.assertEqual((10, 10, 20, 20), self.area.bbox)

    def test_press_x_y_equal_to_release_x_y(self):
        self.area['press'] = 10, 10
        self.area['release'] = 10, 10
        self.assertEqual((10, 10, 10, 10), self.area.bbox)


if __name__ == '__main__':
    unittest.main()
