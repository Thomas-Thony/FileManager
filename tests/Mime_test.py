import unittest
from core.Models.Mime import Mime

class MimeTest(unittest.TestCase):
    def test_get_format(self):
        mime= Mime("image", "jpeg")
        self.assertEqual(mime.get_format() == "image/jpeg", True)
        self.assertEqual(mime.get_format() == "video/jpeg", False)
        self.assertEqual(mime.get_format() == "image/png", False)
        

if __name__ == '__main__':
    unittest.main()