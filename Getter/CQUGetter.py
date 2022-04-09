from typing import Callable

from mycqu.auth import login as mycqu_login
from requests import Session

from functools import wraps

from CQUGetterException import AuthserverUnlogin, AuthserverUnaccess


class CQUGetter:
    def __init__(self, session_ctor: Callable[[], Session] = Session):
        self.session = session_ctor()
        self._is_login = False
        self._is_access = False

    @staticmethod
    def need_login(func):
        @wraps(func)
        def wrapped_function(self, *args, **kwargs):
            self.is_login()
            return func(self, *args, **kwargs)
        return wrapped_function

    @staticmethod
    def need_login_and_access(func):
        @wraps(func)
        def wrapped_function(self, *args, **kwargs):
            self.is_login()
            self.is_access()
            return func(self, *args, **kwargs)
        return wrapped_function

    def login(self, auth: str, password: str):
        self._authserver_login_by_mycqu(auth, password)
        self._is_login = True

    def is_login(self):
        if not self._is_login:
            raise AuthserverUnlogin

    def is_access(self):
        if not self._is_access:
            raise AuthserverUnaccess

    def _authserver_login_by_mycqu(self, auth: str, password: str):
        mycqu_login(self.session, auth, password, kick_others=True)

    def __del__(self):
        self.session.close()
