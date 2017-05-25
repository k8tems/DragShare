import unittest
import main


class TestGetAreaSrc(unittest.TestCase):
    def test_press_x_y_less_than_release_x_y(self):
        self.assertEqual((10, 10), main.get_area_src((10, 10), (20, 20)))

    def test_press_y_greater_than_release_y(self):
        self.assertEqual((10, 20), main.get_area_src((10, 30), (20, 20)))

    def test_press_y_y_greater_than_release_y(self):
        self.assertEqual((10, 10), main.get_area_src((20, 20), (10, 10)))


class TestGetAreaDest(unittest.TestCase):
    def test_press_x_y_less_than_release_x_y(self):
        self.assertEqual((20, 20), main.get_area_dest((10, 10), (20, 20)))

    def test_press_y_greater_than_release_y(self):
        self.assertEqual((20, 30), main.get_area_dest((10, 30), (20, 20)))

    def test_press_y_y_greater_than_release_y(self):
        self.assertEqual((20, 20), main.get_area_dest((20, 20), (10, 10)))


if __name__ == '__main__':
    unittest.main()
