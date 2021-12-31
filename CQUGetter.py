from typing import List, Dict, Any, Union, Optional
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


class CQUGetter:
    """
    将mycqu和selenium+proxy方案实现的重庆大学各类信息查询类
    目前仅支持chromedriver
    """
    def __init__(self, use_selenium=False, debug=False) -> None:
        """
        :param use_selenium: 是否使用selenium+proxy方案
        :param debug: 是否显示selenium浏览器界面
        """
        self.is_success = False     # 用于确定是否已经登陆
        self.use_selenium = use_selenium        # 用于选择是否要调用selenium的方法

        if self.use_selenium:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_server = Service('/usr/bin/chromedriver')
            self.server = Server('./CQU321/browsermob-proxy-2.1.4/bin/browsermob-proxy')
            self.server.start()
            self.proxy = self.server.create_proxy()
            chrome_options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
            chrome_options.add_argument('--ignore-certificate-errors')

            if not debug:
                chrome_options.add_argument('--headless')

            # 这里有在服务器部署时出现的玄学错误，当我没有显示指定chromedriver位置时，运行报错，因此建议指定一下driver位置
            self.driver = webdriver.Chrome(options=chrome_options, service=chrome_server)
        else:
            self.session = None

    def login(self, username: str, password: str) -> bool:
        """

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
                return True
        else:
            try:
                self.session = Session()
                login(self.session, username, password)
                access_mycqu(self.session)
            except:
                self.is_success = False
                return False
            else:
                self.is_success = True
                return True

    def get_score(self, need_all=False):
        if not self.is_success:
            return
        if self.use_selenium:
            # TODO:将selenium成绩查询功能进行完全迁移
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
                # data = get_score_raw(self.session)
                score = Score.fetch(self.session)
                if not need_all:
                    now_session = CQUSession.fetch()[1]
                    score = [item for item in score if item.session == now_session]
            except:
                return

        return score

    def get_exam(self, sid):
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
                        # exams = _explain_response(data,
                        #                                ['roomName', 'startTime', 'endTime', 'courseName', 'courseCode',
                        #                                 'examDate', 'seatNum'])
                        exams = Exam.from_dict(sid)
                        self.proxy.close()
                        self.server.stop()
                        self.driver.quit()
                        return exams
        else:
            exams = Exam.fetch(sid)

            return exams

    def get_courses(self, sid):
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
                ActionChains(driver=self.driver).send_keys(sid).perform()
                # TODO: 将手动延时修改为自动延时
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
                        # courses = _explain_response(data, ['weekDayFormat', 'courseName', 'courseCode', 'classNbr',
                        #                                         'roomName', 'instructorName', 'teachingWeekFormat',
                        #                                         'periodFormat', 'credit'])
                        courses = CourseTimetable.from_dict(data)
                        self.proxy.close()
                        self.server.stop()
                        self.driver.quit()
                        return courses
        else:
            courses = CourseTimetable.fetch(self.session, sid)
            return courses
