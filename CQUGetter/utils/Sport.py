from typing import Optional, Dict, List

from requests import Session

from bs4 import BeautifulSoup

from CQUGetter.utils.CQUGetterException import InvalidCaptcha, CaptchaIncorrect, LoginFail

TZCS_CAPTCHA_URL = "http://tzcs.cqu.edu.cn/servlet/UpdateDate?method=validateCode"
TZCS_LOGIN_URL = "http://tzcs.cqu.edu.cn/servlet/adminservlet"
TZCS_LIST_URL = "http://tzcs.cqu.edu.cn/student/Historyhealth.jsp"
TZCS_DETAIL_URL = "http://tzcs.cqu.edu.cn/SportWeb/health_info/listdetalhistroyScore.jsp"


def login_tzcs(session: Session,
               username: str,
               password: str,
               captcha_callback: [[bytes], Optional[str]],
               ):
    captcha_res = session.get(TZCS_CAPTCHA_URL)
    img = captcha_res.content
    captcha = captcha_callback(img)

    if captcha is None or len(captcha) != 4:
        raise InvalidCaptcha

    login_param = {
        'operType': 911,
        'loginflag': 0,
        'loginType': 1,
        'userName': username,
        'passwd': password,
        'validCode': captcha
    }

    login_res = session.post(TZCS_LOGIN_URL, params=login_param)

    if login_res.text != 'success':
        if login_res.text == '验证码错误！':
            raise CaptchaIncorrect
        else:
            raise LoginFail

    login_param['loginType'] = 0
    session.post(TZCS_LOGIN_URL, params=login_param)


def _parse_score_list_html(html: str) -> Optional[List[Dict]]:
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find_all('table')[-1]
    rows = table.find_all('tr')
    if len(rows) > 3:
        rows = rows[3:]
    else:
        return None

    result = []
    for row in rows:
        datas = row.find_all('td')
        assert len(datas) == 10
        form_element = datas[9]
        stu_no_element = form_element.find_all('input')[1]
        result.append({
            'Username': datas[1].text,
            'StuNo': stu_no_element['value'],
            'Sex': datas[3].text,
            'AcademicYear': datas[4].text,
            'Term': datas[5].text,
            'Grade': datas[6].text,
            'Score': datas[7].text,
            'Level': datas[8].text,
        })

    return result


def _parse_score_detail_html(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find_all('table')[-1]
    rows = table.find_all('tr')[3:]

    result = []
    for row in rows:
        datas = row.find_all('td')
        if len(datas) < 5:
            continue
        result.append({
            'Name': datas[1].text.strip(),
            'Result': datas[2].text.strip(),
            'Score': datas[3].text.strip(),
            'Level': datas[4].text.strip(),
        })

    return result


def get_history_score_list(session: Session) -> Optional[List[Dict]]:
    res = session.get(TZCS_LIST_URL)
    if res.text:
        return _parse_score_list_html(res.text)
    else:
        return None


def get_history_score_detail(session: Session, stu_no: str,
                             academic_year: str, term: str, grade_no: str, sex: str) -> Optional[List[Dict]]:
    params = {
        'submit': "查看",
        'studentNo': stu_no,
        'academicYear': academic_year,
        'term': term,
        'gradeNo': grade_no,
        'sex': sex
    }

    res = session.post(TZCS_DETAIL_URL, params=params)
    if res.text:
        return _parse_score_detail_html(res.text)
    else:
        return None
