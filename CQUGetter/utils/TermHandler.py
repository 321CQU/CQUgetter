import datetime
import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

from requests import Session

from CQUGetter.utils.CQUGetterException import TermInfoGetError, TermNotExist


class TermHandler:
    term_info_url = 'https://my.cqu.edu.cn/api/resourceapi/session/info/'
    term_list_url = 'https://my.cqu.edu.cn/api/timetable/optionFinder/session?blankOption=false'
    curr_term_url = 'https://my.cqu.edu.cn/api/resourceapi/session/cur-active-session'
    term_list = []
    curr_term = {}
    last_update_date = datetime.datetime.fromtimestamp(0)

    @staticmethod
    def _set_term_list(session: Session):
        TermHandler.term_list = json.loads(session.get(TermHandler.term_list_url).text)

    @staticmethod
    def _set_curr_term(session: Session):
        res = json.loads(session.get(TermHandler.curr_term_url).text)
        if res.get('status') and res['status'] == 'success':
            res = res['data']
        else:
            raise TermInfoGetError

        TermHandler.curr_term = {
            'year': int(res['year']),
            'term': 0 if res['term'] == '秋' else 1,
            'id': res['id']
        }

    @staticmethod
    def _get_term_name(term_offset: int) -> str:
        temp = term_offset + TermHandler.curr_term['term']
        target_term = temp % 2
        target_year = TermHandler.curr_term['year'] + \
                      int(Decimal(str(temp / 2)).quantize(Decimal('0'), rounding=ROUND_HALF_UP))
        target_term = '春' if target_term else '秋'

        return str(target_year) + '年' + target_term

    @staticmethod
    def get_term_id(session: Session, term_offset: int) -> str:
        if (datetime.datetime.now() - TermHandler.last_update_date).days > 30:
            TermHandler._set_term_list(session)
            TermHandler._set_curr_term(session)
        target_term_name = TermHandler._get_term_name(term_offset)

        result = list(filter(lambda x: x['name'] == target_term_name, TermHandler.term_list))
        if len(result):
            return result[0]['id']
        else:
            raise TermNotExist

    @staticmethod
    def get_term_info(session: Session, term_id: str) -> Dict:
        url = TermHandler.term_info_url + term_id
        res = json.loads(session.get(url).text)
        if res.get('status') and res['status'] == 'success':
            res = res['data']
        else:
            raise TermInfoGetError

        return {
            'Term': res['year'] + res['term'],
            'StartDate': res['beginDate'],
            'EndDate': res['endDate']
        }
