import requests
import warnings
import json
import time
import pandas as pd


def get_headers(cookie):
    '''
    根据cookies构建消息请求头
    '''
    myheaders = {
        'Content-Type': 'application/json',
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        'vpn-12-o2-uims.jlu.edu.cn': '',
    }
    return myheaders


def get_course(myheaders):
    '''
    return:
    pd.DataFrame.from_dict(course_list): 已选以及未选的课程列表
    course_map: 未选的课程以及编号，该编号用于选课
    '''

    course_html = 'https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/ntms/service/res.do?vpn-12-o2-uims.jlu.edu.cn'
    deHtml = 'https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/ntms/service/res.do?vpn-12-o2-uims.jlu.edu.cn'
    course_dict = {
        'tag': "lessonSelectLog@selectStore",
        'branch': "default",
        'params': {'splanId': 20}  # 注意，此参数每学期不同会发生变化，不一定一直适用！！需要进行修改维护！！通过分析选课的请求可以得到！！
    }
    deInfo = {
        'tag': "lessonSelectLogTcm@selectGlobalStore",
        'branch': "self",
        'params': {'lslId': 0, 'myCampus': "Y"}  # Y选课, N退课
    }
    type_dict = {3060: '必修课', 3061: '选修课', 3062: '限选课', 3063: '未知', 3064: '选修课', 3065: '校选修课'}
    course_list = []
    course_map = {}

    # 获取所有课程
    course_json = json.dumps(course_dict)
    course_result = requests.post(course_html, data=course_json, headers=myheaders, allow_redirects=True, verify=False)
    course_detail = json.loads(course_result.text)

    # 根据获取的json格式数据转存数据
    for i in range(len(course_detail['value'])):
        single = {}
        single['课程名称'] = course_detail['value'][i]['lesson']['courseInfo']['courName']
        single['选否'] = course_detail['value'][i]['selectResult']
        single['选课类型'] = type_dict[course_detail['value'][i]['applyPlanLesson']['selectType']]
        lslId = course_detail['value'][i]['lslId']
        deInfo['params']['lslId'] = lslId
        de_json = json.dumps(deInfo)
        de_result = requests.post(deHtml, data=de_json, headers=myheaders, allow_redirects=True, verify=False)
        de = json.loads(de_result.text)
        single['选课编号'] = de['value'][0]['lsltId']
        course_list.append(single)
        if course_detail['value'][i]['selectResult'] == 'N':
            course_map[single['选课编号']] = single['课程名称']  # 仅存储未选课程的编号，其他可以自行查看
        time.sleep(0.5)  # 调速，防止被封
    return pd.DataFrame.from_dict(course_list), course_map


def fuck_course(lsltId_list, course_map, myheaders):
    '''
    根据lsltId_list中的课程id进行抢课
    '''

    course_detail = {
        'lsltId': 0,
        'opType': "Y"  # Y选课, N退课
    }
    course_html = 'https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/ntms/action/select/select-lesson.do?vpn-12-o2-uims.jlu.edu.cn'
    i = 1
    while True:  # 抢课轮数，暂未设置所有课程抢课成功后终止，需要手动终止
        try:
            for lsltId in lsltId_list:  # 抢每一门课
                course_detail['lsltId'] = lsltId
                detail_json = json.dumps(course_detail)
                result = requests.post(course_html, data=detail_json, headers=myheaders, allow_redirects=True,
                                       verify=False)
                info = json.loads(result.text)
                print(info)
                if info['count'] == 1:
                    print('第' + str(i) + '次：' + str(course_map[str(lsltId)]) + '  抢课成功')  # 可用于捡漏
                else:
                    print('第' + str(i) + '次：' + str(course_map[str(lsltId)]) + '  抢课失败  原因：' + info['msg'])
                # time.sleep(1)    ######################  调速  ######################
            i += 1
        except Exception as e:  # 可能服务器突然没响应
            print(e)


def main():
    cookie = 'wengine_vpn_ticket=33da71016633c03c; refresh=1'  # ...为你自己的cookie内容
    myheaders = get_headers(cookie)  # 获取请求头
    df_course, course_map = get_course(myheaders)  # 获取待抢课程编号
    print(course_map)  # 输出course_map，根据其内容选择要抢的课程所对应的编号
    lsltId_list = [71576210]
    fuck_course(lsltId_list, course_map, myheaders)  # 开始抢课


if __name__ == '__main__':
    main()
