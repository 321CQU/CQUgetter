from typing import Dict

from requests import Session

from CQUGetter import CQUGetter
from CQUGetterParser import CQUGetterParser
from CQUGetterException import CardUnaccess

from mycqu.card import *

__all__ = ('CardGetter',)


class CardGetter(CQUGetter):
    def __init__(self):
        super().__init__()

    def is_access(self):
        if not self._is_access:
            raise CardUnaccess

    @staticmethod
    def _card_access_by_mycqu(session: Session):
        access_card(session)

    @CQUGetter.need_login
    def access(self):
        CardGetter._card_access_by_mycqu(self.session)
        self._is_access = True

    @CQUGetter.need_login_and_access
    def get_fees_by_mycqu(self, isHuXi: bool, room: str) -> Dict:
        return CQUGetterParser.parse_energy_fee_object(EnergyFees.fetch(self.session, isHuXi, room), isHuXi)

    @CQUGetter.need_login_and_access
    def get_card_by_mycqu(self):
        card = Card.fetch(self.session)
        bills = card.fetch_bills(self.session)
        result = CQUGetterParser.parse_card_object(card)
        result['Bills'] = list(map(CQUGetterParser.parse_bill_object, bills))
        return result





