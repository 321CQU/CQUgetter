import unittest

from Getter.CardGetter import CardGetter
from test.testCQUGetter import CQUGetterTestCase


class CardGetterTestCase(CQUGetterTestCase, unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.getter = CardGetter()

    @CQUGetterTestCase.login_test
    def test_card_access(self):
        self.getter.access()
        self.getter.is_access()

    @CQUGetterTestCase.login_and_access_test
    def test_get_fee_in_HuXi(self):
        fees = self.getter.get_fees_by_mycqu(True, "b5321")
        self.assertIsNotNone(fees)

    @CQUGetterTestCase.login_and_access_test
    def test_get_fee_in_ABC_campus(self):
        fees = self.getter.get_fees_by_mycqu(False, "a6s201")
        self.assertIsNotNone(fees)


    @CQUGetterTestCase.login_and_access_test
    def test_get_card(self):
        card = self.getter.get_card_by_mycqu()
        self.assertIsInstance(card, dict)
        self.assertIn('Amount', card)


if __name__ == '__main__':
    unittest.main()
