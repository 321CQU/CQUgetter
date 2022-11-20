import unittest
from typing import List, Tuple, Dict

from CQUGetter.Getter.LibGetter import LibGetter
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

    @CQUGetterTestCase.login_and_access_test
    def test_renew_book(self):
        books = self.getter.renew_book("123456")
        self.assertIsInstance(books, Tuple)

    @CQUGetterTestCase.login_and_access_test
    def test_search_book(self):
        books_1 = self.getter.search_book("操作系统", 1, False)
        books_2 = self.getter.search_book("深度学习", 2)
        self.assertEqual(len(books_1), 10)
        self.assertEqual(len(books_2), 10)

    @CQUGetterTestCase.login_and_access_test
    def test_get_book_pos(self):
        book_id = '31522336328757'
        result = self.getter.get_book_pos(book_id)
        self.assertIsInstance(result, List)

    @CQUGetterTestCase.login_and_access_test
    def test_get_book_detail(self):
        book_id = '31522336328757'
        result = self.getter.get_book_detail(book_id)
        self.assertIsInstance(result, Dict)


if __name__ == '__main__':
    unittest.main()
