import unittest
import drag


class TestArea(unittest.TestCase):
    def create_area(self, *args, **kwargs):
        return drag.DragArea(*args, **kwargs)

    def test_init_pos_x_y_less_than_cur_pos_x_y(self):
        drag_area = self.create_area((10, 10), (20, 20))
        self.assertEqual((10, 10, 20, 20), drag_area.bbox)
        self.assertEqual(10, drag_area.width)
        self.assertEqual(10, drag_area.height)

    def test_init_pos_y_greater_than_cur_pos_y(self):
        drag_area = self.create_area((10, 30), (20, 20))
        self.assertEqual((10, 20, 20, 30), drag_area.bbox)
        self.assertEqual(10, drag_area.width)
        self.assertEqual(10, drag_area.height)

    def test_init_pos_x_greater_than_cur_pos_x(self):
        drag_area = self.create_area((30, 10), (20, 20))
        self.assertEqual((20, 10, 30, 20), drag_area.bbox)
        self.assertEqual(10, drag_area.width)
        self.assertEqual(10, drag_area.height)

    def test_init_pos_x_y_greater_than_cur_pos_x_y(self):
        drag_area = self.create_area((20, 20), (10, 10))
        self.assertEqual((10, 10, 20, 20), drag_area.bbox)
        self.assertEqual(10, drag_area.width)
        self.assertEqual(10, drag_area.height)

    def test_init_pos_x_y_equal_to_cur_pos_x_y(self):
        drag_area = self.create_area((10, 10), (10, 10))
        self.assertEqual((10, 10, 10, 10), drag_area.bbox)
        self.assertEqual(0, drag_area.width)
        self.assertEqual(0, drag_area.height)


if __name__ == '__main__':
    unittest.main()
