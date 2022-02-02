# CQUgetter
对pymycqu和基于selenium+proxy实现的重庆大学学生相关信息查询功能

目前同时支持研究生用户成绩查询以及本科生课表、成绩、排考、下学期选课结果查询

### 所使用的库
mycqu、beautifulsoup4、selenium（本方案目前只支持chromedriver）、browsermobproxy

后三者用于支持selenium+proxy方案（可以无视教务网接口变化）本方案同时对第一个库的支持项目进行了封装和拓展

### 使用说明
1. 直接复制CQUGetter.py文件
2. 导入CQUGetter，创建CQUGetter对象，如需使用selenium+proxy方案，设置use_selenium为True，并同时设置对应的driver_path、proxy_path，如果需要显示selenium图形界面，设置debug为True
3. 先调用login方法，通过用户账号密码登陆（研究生登陆调用pg_login方法）
4. 根据需要继续调用对应方法，例如获取成绩数据则调用get_score方法（研究生成绩查询调用pg_get_score方法）

### 特别鸣谢
Hagb 的项目 <https://github.com/Hagb/pymycqu> 本项目目前所返回的相关对象定义均出自pymycqu的定义
