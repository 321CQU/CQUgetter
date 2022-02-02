# CQUgetter
对pymycqu和基于selenium+proxy实现的重庆大学相关信息查询功能

### 使用说明
1. 直接复制CQUGetter.py文件
2. 导入CQUGetter，创建CQUGetter对象，如需使用selenium+proxy方案，设置use_selenium为True，并同时设置对应的driver_path、proxy_path，如果需要显示selenium图形界面，设置debug为True
3. 先调用login方法，通过用户账号密码登陆（研究生登陆调用pg_login方法）
4. 根据需要继续调用对应方法，例如获取成绩数据则调用get_score方法（研究生成绩查询调用pg_get_score方法）

### 特别鸣谢
Hagb 的项目 <https://github.com/Hagb/pymycqu> 本项目目前所返回的相关对象定义均出自pymycqu的定义
