# fuck_course

**吉林大学抢课爬虫，吉林大学uims抢课**，基于`vpns.jlu.edu.cn`，不是`uims.jlu.edu.cn`，（两者并无差别，只是vpns可以校外登陆），所以获取cookie时必须在[vpns的教务系统](https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/ntms/)上获取。基于vpns页面的好处是捡漏课程时可以挂在服务器上，且便于校外操作。并没有实现输入账号密码直接登陆并获取cookies，可改进，目前需要手工获取cookies。



## 参数及函数说明：

1. cookie： 登陆[教务系统](https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/ntms/)时返回的cookie

2. get_headers(cookie)

   根据cookies构建消息请求头

   - 返回值：

     myheaders：根据cookies构造好的请求头

3. get_course(myheaders)

   用于获取加入选课页面课程的课程id，根据此id提交post请求抢课

    - 参数：

      myheaders：get_headers(cookie)所返回的请求头

    - 返回值：

        pd.DataFrame.from_dict(course_list): 已选以及未选的课程列表

        course_map: 未选的课程以及编号，该编号用于选课

4. fuck_course(lsltId_list, course_map, myheaders)

   根据lsltId_list中的课程id进行抢课

   - 参数：

     lsltId_list：所有待抢课程id的列表

     course_map：get_course(myheaders)返回的course_map

     myheaders：get_headers(cookie)所返回的请求头

     

## 具体用法：

```python
cookie = 'wengine_vpn_ticket=................; refresh=1'    # ...为你自己的cookie内容
myheaders = get_headers(cookie)    # 获取请求头
df_course, course_map = get_course(myheaders)     # 获取待抢课程编号
print(course_map)    # 输出course_map，根据其内容选择要抢的课程所对应的编号
lsltId_list = [71575961, 71978271]    # 要抢的课程列表
fuck_course(lsltId_list, course_map, myheaders)    # 开始抢课
```





## 注意事项

1. cookie暂时需要手工登陆[vpns的教务系统](https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/ntms/)获取

2. ```python
   course_dict = {
       'tag': "lessonSelectLog@selectStore", 
       'branch': "default", 
       'params': {'splanId': 20}   # 
   }
   ```

   此为get_course(myheaders)中的代码段，其中的'splanId'可能随着不同学期选课发生变化，需要自行获取，例如20年下学期2月份值为10，20年上学期7月份值为20

3. 附：测试用例以及部分错误
  
    ```python
    # 测试用例以及部分错误
    course_detail = {
        'lsltId': "70228928",    
        'opType': "N"    # Y选课, N退课
    }
    detail_json = json.dumps(course_detail)
    course_html = 'https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/ntms/action/select/select-lesson.do?vpn-12-o2-uims.jlu.edu.cn'
    for i in range(1,3):
        try:
            result = requests.post(course_html, data = detail_json, headers = myheaders, allow_redirects=True, verify=False)
            info = json.loads(result.text)
            if info['count'] == 1:
                print('第' + str(i) + '次：抢课成功')    # 可用于捡漏
                break
            else:
                print('第' + str(i) + '次：失败  原因：'+ info['msg'])
        except Exception as e:    # 可能服务器突然没响应
            print(e)
        time.sleep(5)    # 自动调速
    
        
    '''    
    {"count":0,"errno":2080,"items":null,"msg":"班级人数已经到达上限","status":-12}
    {"count":1,"errno":0,"items":["S"],"msg":"","status":0}
    {"count":0,"errno":1995,"items":null,"msg":"上课时间冲突，不能选课","status":-6}
    {'count': 0, 'errno': -3, 'items': None, 'msg': '权限不足，您不能执行此操作或者获取数据', 'status': -3}
    {'count': 0, 'errno': 1931, 'items': None, 'msg': '尚未开始选课或者阶段不对', 'status': -12}
    
    {'applyPlanLesson': {'aplId': 524009,
      'planDetail': {'credit': 2},    # 学分
      'testForm': 3091,
      'selectType': 3065,    # 选课类型
      'isReselect': 'N'},    # 选否
     'notes': None,    # 选课反馈
     'selLssgCnt': 0,
     'replyTag': None,    # 反馈备注
     'selectResult': 'N',    # 选否
     'lslId': 50245283,
     'lesson': {'totalClassHour': 30,
      'teachSchool': {'schoolName': '通信工程学院'},
      'lessonId': 67787,
      'courseInfo': {'courType2': 3040, 'courseId': 27121, 'courName': '医用机器人专题'}},
     'sumLssgCnt': 1}
    ''' 
    ```

