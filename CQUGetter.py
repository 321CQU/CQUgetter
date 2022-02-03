from typing import List, Dict, Any, Union, Optional, Callable

from bs4 import BeautifulSoup

from mycqu.auth import login
from mycqu.mycqu import access_mycqu
from mycqu.exam import Exam
from mycqu.course import CourseTimetable, CQUSession
from mycqu.score import Score

from requests import Session

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browsermobproxy import Server

import time
import requests
import json
import re


class CQUGetter:
    """
    将mycqu和selenium+proxy方案实现的重庆大学各类信息查询类
    目前仅支持chromedriver
    """

    def __init__(self, sid: str = None, driver_path: str = '/usr/bin/chromedriver',
                 proxy_path: str = './CQU321/browsermob-proxy-2.1.4/bin/browsermob-proxy', use_selenium=False,
                 debug: bool = False,
                 session_ctor: Callable[[], Session] = Session) -> None:
        """
        :param use_selenium: 是否使用selenium+proxy方案
        :param debug: 是否显示selenium浏览器界面
        :param driver_path: webdriver存放的地址
        :param proxy_path: proxy所在的位置
        :param session_ctor: :class:`Session` 对象的构造器
        """
        self.sid = sid
        self.is_success = False  # 用于确定是否已经登陆
        self.use_selenium = use_selenium  # 用于选择是否要调用selenium的方法
        self.session_ctor = session_ctor

        if self.use_selenium:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_server = Service(driver_path)
            self.server = Server(proxy_path)
            self.server.start()
            self.proxy = self.server.create_proxy()
            chrome_options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
            chrome_options.add_argument('--ignore-certificate-errors')  # 避免访问https网站时chromedriver报错的问题

            if not debug:
                chrome_options.add_argument('--headless')

            # 这里有在服务器部署时出现的玄学错误，当我没有显示指定chromedriver位置时，运行报错，因此建议指定一下driver位置
            self.driver = webdriver.Chrome(options=chrome_options, service=chrome_server)
        else:
            self.session = None

    def login(self, username: str, password: str) -> bool:
        """
        统一身份认证登陆

        :param username: 统一身份认证账号
        :param password: 统一身份认证密码
        :return: is_success: 是否登陆成功
        """
        if self.use_selenium:
            self.driver.get(
                'http://authserver.cqu.edu.cn/authserver/login?service=http%3A%2F%2Fmy.cqu.edu.cn%2Fauthserver%2Fauthentication%2Fcas')
            username_element = self.driver.find_element(By.ID, 'username')
            password_element = self.driver.find_element(By.ID, 'password')
            # submit_element = driver.find_element(By.CLASS_NAME, 'auth_login_btn primary full_width')
            username_element.send_keys(username)
            password_element.send_keys(password + Keys.ENTER)
            # TODO:验证码出现时获取并重试登陆
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'content-blcok')))
            except:
                self.is_success = False
                return False
            else:
                self.is_success = True
        else:
            try:
                self.session = self.session_ctor()
                login(self.session, username, password)
                access_mycqu(self.session)
            except:
                self.is_success = False
                return False
            else:
                self.is_success = True
        return True

    def pg_login(self, username: str, password: str) -> bool:
        """
        研究生账号登陆

        :param username: 研究生学号
        :param password: 密码
        :return: 登陆成功返回true，否则返回false
        """
        self.session = self.session_ctor()
        data = {'userId': username, 'password': password, 'userType': 'student'}
        login_page = self.session.post(url='http://mis.cqu.edu.cn/mis/login.jsp', data=data)
        soup = BeautifulSoup(login_page.content, 'lxml')
        meta = soup.find('meta')['content']
        url = re.search(r'url=.*$', meta).group()
        if url[4:] == 'student.jsp':
            self.is_success = True
            return True
        else:
            self.is_success = False
            return False

    def get_score(self, need_all: bool = False) -> Union[List[Score], None]:
        """
        从教务网所登陆账号的成绩

        :param need_all: 是否获取所有学期的成绩
        :return: 查询成功Score的列表，失败返回None
        """
        if not self.is_success:
            return
        if self.use_selenium:
            try:
                self.driver.get('https://my.cqu.edu.cn/sam')
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'stu-sam-view-content')))
                token = self.driver.execute_script('return localStorage.getItem("cqu_edu_ACCESS_TOKEN");')
                assess_token = "Bearer " + token[1:-1]
            except:
                return
            else:
                headers = {
                    'Referer': 'https://my.cqu.edu.cn/sam/home',
                    'User-Agent': 'User-Agent:Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
                    'Authorization': assess_token
                }
                res = requests.get('http://my.cqu.edu.cn/api/sam/score/student/score', headers=headers)
                data = json.loads(res.content)['data']
                score = []
                for term, courses in data.items():
                    for course in courses:
                        score.append(Score.from_dict(course))
                    if not need_all:
                        break
        else:
            try:
                score = Score.fetch(self.session)
                if not need_all:
                    now_session = CQUSession.fetch()[1]
                    score = [item for item in score if item.session == now_session]
            except:
                return

        return score

    def pg_get_score(self) -> Union[List[Dict], None]:
        """
        获取登陆的研究生账户的成绩

        :return: 成功时返回成绩字典的列表，失败返回None
        """
        if not self.is_success:
            return
        score_page = self.session.get('http://mis.cqu.edu.cn/mis/student/plan/view.jsp')

        soup = BeautifulSoup(score_page.content, 'lxml')
        tables = soup.find_all('table')
        scores = tables[2].find_all('tr')
        del scores[0]
        score_log = []
        for score in scores:
            score_info = score.find_all('td')
            temp_list = []
            for info in score_info:
                info = info.text.strip()
                info = info.replace('\n', '')
                temp_list.append(info)
            if temp_list[7] == '':
                continue
            temp = {
                'Cid': temp_list[1],
                'Cname': temp_list[2],
                'Credit': temp_list[3],
                'Term': temp_list[5],
                'Year': temp_list[6],
                'Score': temp_list[7],
            }
            score_log.append(temp)
        return score_log

    def get_exam(self) -> Union[List[Exam], None]:
        """
        获取考试安排

        :return: 查询成功返回Exam对应的列表，失败返回None
        """
        if not self.is_success:
            return
        if self.use_selenium:
            self.proxy.new_har(options={'captureHeaders': True, 'captureContent': True})
            try:
                self.driver.get('https://my.cqu.edu.cn/exam/home')
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'stu-exam-modal')))
            except:
                return
            else:
                result = self.proxy.har
                for entry in result['log']['entries']:
                    _url = entry['request']['url']
                    if "/api/exam/examTask/get-student-exam-list-outside" in _url:
                        _response = entry['response']
                        _content = _response['content']
                        _result = json.loads(_content['text'])
                        data = _result['data']['content']
                        exams = [Exam.from_dict(exam) for exam in data]
                        self.proxy.close()
                        self.server.stop()
                        self.driver.quit()
                        return exams
        else:
            exams = Exam.fetch(self.sid)

            return exams

    def get_courses(self) -> Union[List[CourseTimetable], None]:
        """
        获取登陆用户所拥有课程

        :return: 查询成功返回CourseTimetable的列表，失败返回None
        """
        if not self.is_success:
            return
        if self.use_selenium:
            self.proxy.new_har(options={'captureHeaders': True, 'captureContent': True})
            try:
                self.driver.get('https://my.cqu.edu.cn/tt/AllCourseSchedule')
                list_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="app"]/div/section/section/section/main/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div/div'))
                )
                ActionChains(driver=self.driver).click(list_element).perform()

                ActionChains(driver=self.driver).move_by_offset(0, 240).perform()
                ActionChains(driver=self.driver).click().perform()
                input_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="app"]/div/section/section/section/main/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div[1]/div[1]/div[2]/div')))
                ActionChains(driver=self.driver).click(input_element).perform()
                ActionChains(driver=self.driver).send_keys(self.sid).perform()
                ActionChains(driver=self.driver).move_by_offset(0, 80).perform()
                time.sleep(2)
                ActionChains(driver=self.driver).click().perform()
            except:
                return
            else:
                result = self.proxy.har
                for entry in result['log']['entries']:
                    _url = entry['request']['url']
                    if "/api/timetable/class/timetable/student/table-detail" in _url:
                        _response = entry['response']
                        _content = _response['content']
                        _result = json.loads(_content['text'])
                        data = _result['classTimetableVOList']
                        courses = [CourseTimetable.from_dict(timetable) for timetable in data
                                   if timetable["teachingWeekFormat"]
                                   ]
                        self.proxy.close()
                        self.server.stop()
                        self.driver.quit()
                        return courses
        else:
            courses = CourseTimetable.fetch(self.session, self.sid)
            return courses

    def get_enrollment(self) -> Optional[List[CourseTimetable]]:
        """
        获取下学期已选课表数据

        :return: 下学期课程的列表
        """
        if self.is_success:
            if self.use_selenium:
                # TODO:完善用selenium获取信息的部分
                return None
            else:
                try:
                    res = self.session.get('https://my.cqu.edu.cn/api/enrollment/timetable/student/{self.sid}')
                    data = json.loads(res.content)['data']
                    # 从选课api获取的数据中，教师姓名位置稍有不同
                    data['instructorName'] = data['classTimetableInstrVOList'][0]['instructorName']
                    courses = [CourseTimetable.from_dict(timetable) for timetable in data
                               if timetable["teachingWeekFormat"]
                               ]
                except:
                    courses = None
                return courses
