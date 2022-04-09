import unittest
from typing import List, Dict

from Getter.DeanGetter import DeanGetter
from test.testCQUGetter import CQUGetterTestCase


class DeanGetterTestCase(CQUGetterTestCase, unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.getter = DeanGetter()

    @CQUGetterTestCase.login_and_access_test
    def test_get_score(self):
        scores = self.getter.get_score_by_mycqu()
        self.assertIsInstance(scores, List)

    def test_get_exam(self):
        exams = self.getter.get_exam_by_mycqu(self.sid)
        self.assertIsInstance(exams, List)

    @CQUGetterTestCase.login_and_access_test
    def test_get_course(self):
        self.assertIsInstance(self.getter.get_course_by_mycqu(self.sid), List)

    @CQUGetterTestCase.login_and_access_test
    def test_get_enrollment(self):
        temp = self.getter.get_enrollment(self.sid)
        self.assertIsInstance(temp, List)

    @CQUGetterTestCase.login_and_access_test
    def test_get_gpa_ranking(self):
        temp = self.getter.get_gpa_ranking()
        self.assertIsInstance(temp, Dict)

    @CQUGetterTestCase.login_and_access_test
    def test_get_person_info(self):
        info = self.getter.get_person_info()
        self.assertIsInstance(info, Dict)


if __name__ == '__main__':
    unittest.main()
