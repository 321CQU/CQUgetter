import unittest
import configparser

from mycqu.exception import IncorrectLoginCredentials, NeedCaptcha

from CQUGetter.Getter.CQUGetter import CQUGetter

from functools import wraps

from CQUGetter.utils.CQUGetterException import Unlogin, Unaccess, AuthserverUnlogin


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
        conn = configparser.ConfigParser()
        conn.read("./test.cfg")

        self.sid = conn.get('ACCOUNT', 'sid')
        self.auth = conn.get('ACCOUNT', 'account')
        self.password = conn.get('ACCOUNT', 'password')

    def test_login_with_incorrect_account(self):
        with self.assertRaises((IncorrectLoginCredentials, NeedCaptcha)):
            self.getter.login("11111111", "1111111111")


if __name__ == '__main__':
    unittest.main()
