import unittest
import area


class TestArea(unittest.TestCase):
    def setUp(self):
        self.area = area.DragArea()

    def test_init_pos_x_y_less_than_cur_pos_x_y(self):
        self.area['init_pos'] = 10, 10
        self.area['cur_pos'] = 20, 20
        self.assertEqual((10, 10, 20, 20), self.area.bbox)
        self.assertEqual(10, self.area.width)
        self.assertEqual(10, self.area.height)

    def test_init_pos_y_greater_than_cur_pos_y(self):
        self.area['init_pos'] = 10, 30
        self.area['cur_pos'] = 20, 20
        self.assertEqual((10, 20, 20, 30), self.area.bbox)
        self.assertEqual(10, self.area.width)
        self.assertEqual(10, self.area.height)

    def test_init_pos_x_greater_than_cur_pos_x(self):
        self.area['init_pos'] = 30, 10
        self.area['cur_pos'] = 20, 20
        self.assertEqual((20, 10, 30, 20), self.area.bbox)
        self.assertEqual(10, self.area.width)
        self.assertEqual(10, self.area.height)

    def test_init_pos_x_y_greater_than_cur_pos_y(self):
        self.area['init_pos'] = 20, 20
        self.area['cur_pos'] = 10, 10
        self.assertEqual((10, 10, 20, 20), self.area.bbox)
        self.assertEqual(10, self.area.width)
        self.assertEqual(10, self.area.height)

    def test_init_pos_x_y_equal_to_cur_pos_x_y(self):
        self.area['init_pos'] = 10, 10
        self.area['cur_pos'] = 10, 10
        self.assertEqual((10, 10, 10, 10), self.area.bbox)
        self.assertEqual(0, self.area.width)
        self.assertEqual(0, self.area.height)


if __name__ == '__main__':
    unittest.main()
