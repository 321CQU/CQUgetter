from typing import Dict

from mycqu import access_mycqu
from requests import Session

from CQUGetter.Getter.CQUGetter import CQUGetter
from CQUGetter.Getter.DeanGetter import DeanGetter
from CQUGetter.utils.CQUGetterParser import CQUGetterParser
from CQUGetter.utils.CQUGetterException import CardUnaccess

from mycqu.card import *

__all__ = ('CardGetter',)


class CardGetter(CQUGetter):
    def is_access(self):
        if not self._is_access:
            raise CardUnaccess

    @staticmethod
    def _card_access_by_mycqu(session: Session):
        access_mycqu(session)
        access_card(session)

    @CQUGetter.need_login
    def access(self):
        DeanGetter._authserver_access_by_mycqu(self.session)
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





