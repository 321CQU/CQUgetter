__all__ = ['CQUGetterException', 'Unlogin', 'Unaccess', 'AuthserverUnaccess', 'AuthserverUnlogin',
           'CardUnaccess', 'LibUnaccess', 'TermInfoGetError', 'TermNotExist', 'LoginFail', 'CaptchaIncorrect',
           'InvalidCaptcha',]


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
    当访问lib.cqu.edu.cn时，未进行验证时引发
    """


class LoginFail(CQUGetterException):
    """
    当登陆失败时抛出（可能为账号密码错误，也可能为网络超时）
    """


class TermInfoGetError(CQUGetterException):
    """
    当无法获取学期信息时抛出
    """


class TermNotExist(CQUGetterException):
    """
    搜索目标学期不存在时抛出
    """


class CaptchaIncorrect(CQUGetterException):
    """
    验证码错误时抛出
    """


class InvalidCaptcha(CQUGetterException):
    """
    无效的验证码
    """
