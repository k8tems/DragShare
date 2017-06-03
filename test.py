import unittest
import mock
import drag
import view
import tkinter


class TestCanvasAnimation(unittest.TestCase):
    def setUp(self):
        self.frames = [1, 2, 3, 4, 5]
        self.generate_animation = lambda image: view.Animation(self.frames, 10)
        self.canvas = mock.MagicMock(cur_image_without_effect=6)

        self.root = tkinter.Tk()
        self.root.withdraw()
        self.canvas_animation = view.CanvasAnimation(self.root, self.generate_animation, self.canvas)

        self.root.after(0, self.canvas_animation.on_image_url_requested)

    def get_params_of_set_image(self):
        return [i[0][0] for i in self.canvas.set_image.call_args_list]

    def test(self):
        self.root.after(500, self.root.destroy)
        self.root.mainloop()
        # assert that the expected frames have been displayed
        expected_frames = self.frames * 3
        self.assertEqual(expected_frames, self.get_params_of_set_image()[:len(expected_frames)])

    def test_on_twitter_upload_finished(self):
        self.root.after(500, self.canvas_animation.on_twitter_upload_finished)
        self.root.after(500, self.root.destroy)
        self.root.mainloop()
        # assert that the scaled image is restored
        self.assertEqual(6, self.get_params_of_set_image()[-1])


class TestGetWinfo(unittest.TestCase):
    def test(self):
        self.assertEqual((400, 500), view.get_winfo('200x300+400+500'))


class TestScale(unittest.TestCase):
    def setUp(self):
        self.scale = view.ViewScale((100, 100))

    def test_increase(self):
        self.assertEqual((110, 110), self.scale(1))

    def test_decrease(self):
        self.assertEqual((90, 90), self.scale(-1))

    def test_capped_to_10_percent(self):
        self.assertEqual((10, 10), self.scale(-9))
        self.assertEqual((10, 10), self.scale(-10))


class TestAnimation(unittest.TestCase):
    def test(self):
        ani = view.Animation([1, 2], None)
        self.assertEqual(1, ani.next())
        self.assertEqual(2, ani.next())
        self.assertEqual(1, ani.next())


class TestGenerateFlashingSequence(unittest.TestCase):
    def test(self):
        self.assertEqual([1.0, 1.5, 2.0, 1.5, 1.0], view.generate_flashing_sequence(1.0, 2.0, 0.5))


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
