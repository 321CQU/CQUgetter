import unittest

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover("./")

    unittest.TextTestRunner().run(suite)

