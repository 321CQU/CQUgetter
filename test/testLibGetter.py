import unittest
from typing import List

from Getter.LibGetter import LibGetter
from test.testCQUGetter import CQUGetterTestCase


class LibGetterTestCase(CQUGetterTestCase, unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.getter = LibGetter()

    @CQUGetterTestCase.login_test
    def test_lib_access(self):
        self.getter.access()
        self.getter.is_access()

    @CQUGetterTestCase.login_and_access_test
    def test_get_history_book_list(self):
        books = self.getter.get_borrow_list_by_mycqu(False)
        self.assertIsInstance(books, List)

    @CQUGetterTestCase.login_and_access_test
    def test_get_curr_book_list(self):
        books = self.getter.get_borrow_list_by_mycqu(True)
        self.assertIsInstance(books, List)


if __name__ == '__main__':
    unittest.main()
