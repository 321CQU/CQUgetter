from typing import Callable

from mycqu.auth import login as mycqu_login
from requests import Session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from functools import wraps

from CQUGetter.utils.CQUGetterException import AuthserverUnlogin, AuthserverUnaccess, LoginFail

__all__ = ('CQUGetter',)


class CQUGetter:
    def __init__(self, session_ctor: Callable[[], Session] = Session):
        self.session = session_ctor()
        self._is_login = False
        self._is_access = False
        self._headers = None

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

    def login(self, auth: str, password: str, use_selenium: bool = False):
        if not use_selenium:
            self._authserver_login_by_mycqu(auth, password)
            self._is_login = True
        else:
            self._authserver_login_by_selenium(auth, password, True)

    def is_login(self):
        if not self._is_login:
            raise AuthserverUnlogin

    def is_access(self):
        if not self._is_access:
            raise AuthserverUnaccess

    def set_login_cookie(self, authorization: str):
        self._headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Authorization': authorization,
        }
        self.session.headers.update(self._headers)
        self._is_login = True
        self._is_access = True

    def get_login_cookie(self):
        return self.session.headers.get('authorization')

    def _authserver_login_by_mycqu(self, auth: str, password: str):
        mycqu_login(self.session, auth, password, kick_others=True, keep_longer=True)

    def _authserver_login_by_selenium(self, auth: str, password: str, debug: bool = False):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_server = Service('/usr/bin/chromedriver')
        chrome_options.add_argument('--ignore-certificate-errors')  # 避免访问https网站时chromedriver报错的问题

        if not debug:
            chrome_options.add_argument('--headless')

        # 这里有在服务器部署时出现的玄学错误，当我没有显示指定chromedriver位置时，运行报错，因此建议指定一下driver位置
        driver = webdriver.Chrome(options=chrome_options)  # , service=chrome_server

        driver.get(
            'https://my.cqu.edu.cn/sam')
        username_element = driver.find_element(By.ID, 'username')
        password_element = driver.find_element(By.ID, 'password')
        username_element.send_keys(auth)
        password_element.send_keys(password + Keys.ENTER)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'home')))
        except:
            raise LoginFail
        else:
            authorization = driver.execute_script('return localStorage.getItem("cqu_edu_ACCESS_TOKEN");')
            authorization = 'Bearer ' + authorization[1:-1]
            self.set_login_cookie(authorization)

    def __del__(self):
        self.session.close()

    def access(self):
        pass
