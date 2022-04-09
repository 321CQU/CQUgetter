import json
from typing import List, Dict, Optional, Union

from mycqu import access_mycqu

from .CQUGetter import CQUGetter
from CQUGetterException import AuthserverUnlogin, AuthserverUnaccess
from CQUGetterParser import CQUGetterParser

from mycqu.score import Score, GpaRanking
from mycqu.exam import Exam
from mycqu.course import CourseTimetable, CQUSession


class DeanGetter(CQUGetter):
    def _authserver_access_by_mycqu(self):
        access_mycqu(self.session)

    @CQUGetter.need_login
    def access(self):
        self._authserver_access_by_mycqu()
        self._is_access = True

    @CQUGetter.need_login_and_access
    def get_score_by_mycqu(self) -> List[Dict]:
        return list(map(CQUGetterParser.parse_score_object, Score.fetch(self.session)))

    def get_exam_by_mycqu(self, stu_id: str) -> List[Dict]:
        return list(map(CQUGetterParser.parse_exam_object, Exam.fetch(stu_id)))

    @CQUGetter.need_login_and_access
    def get_course_by_mycqu(self, stu_id: str, cqu_session: Optional[Union[CQUSession, str]] = None) -> List[Dict]:
        return list(map(CQUGetterParser.parse_course_object, CourseTimetable.fetch(self.session, stu_id, cqu_session)))

    @CQUGetter.need_login_and_access
    def get_enrollment(self, stu_id) -> List[Dict]:
        res = self.session.get(f'https://my.cqu.edu.cn/api/enrollment/timetable/student/{stu_id}')
        courses = list(map(CourseTimetable.from_dict, json.loads(res.content)['data']))
        return list(map(CQUGetterParser.parse_course_object, courses))

    @CQUGetter.need_login_and_access
    def get_gpa_ranking(self) -> Dict:
        return CQUGetterParser.parse_gpa_ranking_object(GpaRanking.fetch(self.session))

    @CQUGetter.need_login_and_access
    def get_person_info(self) -> Dict:
        url = "https://my.cqu.edu.cn/authserver/simple-user"
        res = self.session.get(url)
        data = json.loads(res.content)
        return {
            'Sid': data['code'],
            'Name': data['name']
        }

