class CQUGetterException(Exception):
    def __init__(self):
        super().__init__()


class Unlogin(CQUGetterException):
    """
    当未登陆时抛出
    """


class Unaccess(CQUGetterException):
    """
    当未验证时抛出
    """


class AuthserverUnlogin(Unlogin):
    """
    当对象未登陆统一身份认证时引发
    """


class AuthserverUnaccess(Unaccess):
    """
    当对象未验证统一身份认证时引发
    """


class CardUnaccess(Unaccess):
    """
    当访问card.cqu.edu.cn时，未进行验证时引发
    """


class LibUnaccess(Unaccess):
    """
    当访问lib.cqu.edu.cn时，为进行验证时引发
    """
