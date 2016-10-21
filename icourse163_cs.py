#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import re
import os
from bs4 import BeautifulSoup

RefererUrl = input('请粘贴标准Url：')
Cookie = input('请粘贴Cookie缓存：')
headers = {
        'Content-Type':'text/plain',
        'Cookie':Cookie,
        'Host':'mooc.study.163.com',
        'Origin':'http://mooc.study.163.com',
        'Referer':RefererUrl,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }

def get_CourseContent(headers,tid):
    datas = {
        'callCount':'1',
        'scriptSessionId':'${scriptSessionId}190',
        'httpSessionId':'9db1a1b162e34540bafd510d519f9244',
        'c0-scriptName':'CourseBean',
        'c0-methodName':'getLastLearnedMocTermDto',
        'c0-id':'0',
        'c0-param0':'number:{}'.format(str(tid)),
        'batchId':'1476860772584',
        }
    url = 'http://mooc.study.163.com/dwr/call/plaincall/CourseBean.getLastLearnedMocTermDto.dwr'
    try:
        pdata = urllib.parse.urlencode(datas).encode(encoding='UTF8')
        req = urllib.request.Request(url,headers = headers,data = pdata,method = 'POST')
        response = urllib.request.urlopen(req)
        
        soup = BeautifulSoup(response, 'lxml')
        str_content = soup.p.get_text()
        return str_content

    except urllib.request.URLError as e:
        if hasattr(e, "code"):
                 print(e.code)
        if hasattr(e, "reason"):
                 print(e.reason)

def StrContent2Chapter(str_content):
    TermChapter = re.findall('id=(\d+);s.*name="(.*?)";s.*position=-1;',str_content)
    Chapter = []
    for i in range(len(TermChapter)):
        Chapter.append((TermChapter[i][0],TermChapter[i][1].encode('latin-1').decode('unicode-escape')))
    return Chapter
def Chapter2Lesson(str_content,CharpterId):
    TermLesson = re.findall('chapterId=%s;s.*id=(\d+);s.*isTestChecked.*name="(.*?)";s' % CharpterId,str_content)
    Lesson = []
    for i in range(len(TermLesson)):
        Lesson.append((TermLesson[i][0], TermLesson[i][1].encode('latin-1').decode('unicode-escape')))
    return Lesson
def Lesson2Video(str_content,LessonId):
    TermVideo = re.findall('contentId=(\d+);s.*contentType=1;s.*gmtModified=(\d+);s.*id=(\d+);s.*lessonId=%s;s.*name="(.*?)";s.*resourceInfo' % LessonId,str_content)
    Video = []
    for i in range(len(TermVideo)):
        Video.append((TermVideo[i][0],TermVideo[i][1],TermVideo[i][2],TermVideo[i][3].encode('latin-1').decode('unicode-escape')))
    return Video

def get_VideoUrl(headers,tid,contentId,gmtModified,id_num):
    datas = {
        'callCount':'1',
        'scriptSessionId':'${scriptSessionId}190',
        'httpSessionId':'9db1a1b162e34540bafd510d519f9244',
        'c0-scriptName':'CourseBean',
        'c0-methodName':'getLessonUnitLearnVo',
        'c0-id':'0',
        'c0-param0':'number:{}'.format(str(tid)),
        'c0-param1':'number:{}'.format(str(contentId)),
        'c0-param2':'number:1',
        'c0-param3':'number:0',
        'c0-param4':'number:{}'.format(str(id_num)),
        'batchId':'{}'.format(str(gmtModified)),
        }
    url = 'http://mooc.study.163.com/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr?'
    try:
        pdata = urllib.parse.urlencode(datas).encode(encoding='UTF8')
        req = urllib.request.Request(url,headers = headers,data = pdata,method = 'POST')
        response = urllib.request.urlopen(req)
        
        soup = BeautifulSoup(response, 'lxml')
        VideoUrl = re.findall('flvHdUrl="(.*?)";',soup.p.get_text())[0]
        return VideoUrl
    except urllib.request.URLError as e:
       if hasattr(e,"code"):
             print (e.code)
       if hasattr(e,"reason"):
             print (e.reason)

tid = RefererUrl.split('tid=')[-1]
str_content = get_CourseContent(headers,tid)
Chapters = StrContent2Chapter(str_content)
SavePath0 = 'H:\\Course['+tid+']' # 课程保存路径
if not os.path.exists(SavePath0):
    os.mkdir(SavePath0)
for i0 in range(len(Chapters)):  # 章
    str_Chapter = re.sub('[\/\\\:\*\?\"\<\>\|]','_',Chapters[i0][1])
    SavePath1 = os.path.join(SavePath0,'【{}】'.format(i0+1)+str_Chapter)
    if not os.path.exists(SavePath1):
       os.mkdir(SavePath1)
    Lessons = Chapter2Lesson(str_content,Chapters[i0][0])
    for i1 in range(len(Lessons)):  #   节
        video = Lesson2Video(str_content,Lessons[i1][0])
        str_Lesson = re.sub('[\/\\\:\*\?\"\<\>\|]', '_', Lessons[i1][1])
        SavePath2 = os.path.join(SavePath1, '【{}】'.format(i1 + 1) + str_Lesson)
        if not os.path.exists(SavePath2):
            os.mkdir(SavePath2)
        print(SavePath2)
        for i2 in range(len(video)):    #   视频
            VideoUrl = get_VideoUrl(headers,tid,video[i2][0],video[i2][1],video[i2][2])
            VideoName = re.sub(':','_',video[i2][3])
            VideoPathName = SavePath2+'\\【%d】%s.flv' % (i2+1,VideoName)
            urllib.request.urlretrieve(VideoUrl,VideoPathName)
            print(VideoName+' Done!')

