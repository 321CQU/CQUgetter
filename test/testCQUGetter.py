import unittest

from mycqu.auth import IncorrectLoginCredentials, NeedCaptcha

from Getter.CQUGetter import CQUGetter
from CQUGetterException import *

from functools import wraps


class CQUGetterTestCase(unittest.TestCase):
    @staticmethod
    def login_and_access_test(func):
        @wraps(func)
        def wrapped_function(self, *args, **kwargs):
            with self.assertRaises(Unlogin):
                func(self, *args, **kwargs)
            self.getter.login(self.auth, self.password)

            with self.assertRaises(Unaccess):
                func(self, *args, **kwargs)
            self.getter.access()

            return func(self, *args, **kwargs)

        return wrapped_function

    @staticmethod
    def login_test(func):
        @wraps(func)
        def wrapped_function(self, *args, **kwargs):
            with self.assertRaises(AuthserverUnlogin):
                func(self, *args, **kwargs)
            self.getter.login(self.auth, self.password)

            return func(self, *args, **kwargs)

        return wrapped_function

    def setUp(self) -> None:
        self.getter = CQUGetter()
        self.sid = "********"
        self.auth = "********"
        self.password = "*********"

    def test_login_with_incorrect_account(self):
        with self.assertRaises((IncorrectLoginCredentials, NeedCaptcha)):
            self.getter.login("11111111", "1111111111")


if __name__ == '__main__':
    unittest.main()
