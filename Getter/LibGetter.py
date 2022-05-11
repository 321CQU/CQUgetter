from typing import Dict, List, Tuple

from requests import Session

from utils.CQUGetterException import LibUnaccess
from utils.CQUGetterParser import CQUGetterParser
from utils.BookSearchList import BookSearchSet
from .CQUGetter import CQUGetter
from mycqu.library import *

__all__ = ['LibGetter']


class LibGetter(CQUGetter):
    def __init__(self):
        super().__init__()
        self.user_info = None

    def is_access(self) -> None:
        if not self._is_access:
            raise LibUnaccess

    @staticmethod
    def _lib_access_by_mycqu(session: Session) -> Dict:
        return access_library(session)

    @CQUGetter.need_login
    def access(self) -> None:
        self.user_info = self._lib_access_by_mycqu(self.session)
        self._is_access = True

    @CQUGetter.need_login_and_access
    def get_borrow_list_by_mycqu(self, is_curr: bool) -> List[Dict]:
        return list(map(CQUGetterParser.parse_book_info_object, BookInfo.fetch(self.session, self.user_info, is_curr)))

    @CQUGetter.need_login_and_access
    def renew_book(self, book_id: str) -> Tuple[bool, str]:
        statue, info = BookInfo.renew_book(self.session, self.user_info, book_id)
        return statue == 200, info

    @CQUGetter.need_login_and_access
    def search_book(self, keyword: str, page: int = 1, only_huxi: bool = True):
        search_set = BookSearchSet(self.session)
        return search_set.fetch(keyword, page, only_huxi)
