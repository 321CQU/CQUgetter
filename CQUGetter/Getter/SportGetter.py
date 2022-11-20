from typing import Callable, Optional, List, Dict

from requests import Session

from CQUGetter.Getter.CQUGetter import CQUGetter
from CQUGetter.utils.Sport import login_tzcs, get_history_score_detail, get_history_score_list

__all__ = ['SportGetter']


class SportGetter(CQUGetter):
    def __init__(self, captcha_handler: Callable[[str], Optional[str]], session_ctor: Callable[[], Session] = Session):
        super(SportGetter, self).__init__(session_ctor)
        self._captcha_handler = captcha_handler

    def login(self, auth: str, password: str, use_selenium: bool = False):
        login_tzcs(self.session, auth, password, self._captcha_handler)
        self._is_login = True

    @CQUGetter.need_login
    def get_history_score_list(self) -> Optional[List[Dict]]:
        return get_history_score_list(self.session)

    @CQUGetter.need_login
    def get_history_score_detail(self, stu_no: str,
                                 academic_year: str, term: str, grade_no: str, sex: str) -> Optional[List[Dict]]:
        return get_history_score_detail(self.session, stu_no, academic_year, term, grade_no, sex)
