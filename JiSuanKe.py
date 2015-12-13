#!/usr/bin/python
#coding:utf-8

import urllib
import urllib2
import re
import MysqlHelper

class JiSuanKe:
    def __init__(self, url):
        self.url = url

    def removeTab(self, str):
        newstr = str.replace('\t','').replace('\n','').replace(' ','')
        return newstr

    def getCourceUrl(self, url):
        try:
            user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0"
            headers = {'User-Agent':user_agent}
            req = urllib2.Request(url,headers = headers)
            page = urllib2.urlopen(req).read()
            url_chapter = '<a href="(.*)" target="_blank">'
            menu_list = re.findall(url_chapter,page)
            return menu_list
        except urllib2.URLError,e:
            if hasattr(e, 'reason'):
                print "Fail to connect url.Error:"
                return None

    def getPageInfo(self, pageurl):
        try:
            user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0"
            headers = {'User-Agent':user_agent}
            req = urllib2.Request(pageurl,headers = headers)
            page = urllib2.urlopen(req).read()
            return page
        except urllib2.URLError,e:
            if hasattr(e, 'reason'):
                print "Fail to connect url.Error:"
                return None

    def getCourceTime(self, page):
        pattern = re.compile(r'<small class="jsk-fr">(.*?)</small>',re.S)
        courceTime = re.findall(pattern, page)
        if courceTime:
            return courceTime
        else:
            return None

    def getCourceName(self, page):
        pattern = re.compile(r'<h1>(.*?)</h1>',re.S)
        courceName=re.findall(pattern, page)
        if courceName:
            return courceName
        else:
            return None

    def getPeopleNum(self, page):
        pattern = re.compile(r'<small>(.*?)</small>', re.S)
        peopleNum = re.findall(pattern, page)
        if peopleNum:
            return peopleNum
        else:
            return None

    def getInfo(self, page):
        pattern = re.compile('<span class="chapter-index">(.*?)</span><span class="chapter-title">(.*?)</span>.*?<ul class="chapter-lessons">(.*?)</ul>',re.S)
        courceInfo = re.findall(pattern, page)
        if courceInfo:
            return courceInfo
        else:
            return None

    def getBrief_1(self, page):
        pattern = re.compile(r'<div class="jsk-panel-bd syllabus">.*?>.*?>.*?>.*?>(.*?)</p>.*?>(.*?)</p>',re.S)
        groups = re.search(pattern, page)
        if groups == None:
            return None
        value = groups.group(0)
        brief = re.findall(pattern, value)
        if brief:
            return brief
        else:
            return None

    def getBrief(self, page):
        pattern = re.compile(r'<div class="jsk-panel-bd syllabus">.*?>.*?>.*?>.*?>(.*?)</p>',re.S)
        groups = re.search(pattern, page)
        if groups == None:
            return None
        value = groups.group(0)
        brief = re.findall(pattern, value)
        #brief = re.findall(pattern, page)
        if brief:
            return brief
        else:
            return None

    def getBrief_3(self, page):
        pattern = re.compile(r'<div class="jsk-panel-bd syllabus">.*?>.*?>.*?>.*?>(.*?)</p>.*?>(.*?)</p>.*?>(.*?)</p>',re.S)
        groups = re.search(pattern, page)
        if groups == None:
            return None
        value = groups.group(0)

        brief = re.findall(pattern, value)
        #brief = re.findall(pattern, page)
        if brief:
            return brief
        else:
            return None

    def getBrief_4(self, page):
        pattern = re.compile(r'<div class="jsk-panel-bd syllabus">.*?>.*?>.*?><p>(.*?)</p>(.*?)</ul>',re.S)
        groups = re.search(pattern, page)
        if groups == None:
            return None
        value = groups.group(0)
        brief = re.findall(pattern, value)
        #brief = re.findall(pattern, page)
        if brief:
            return brief
        else:
            return None

    def getBrief_5(self, page):
        pattern = re.compile(r'<div class="jsk-panel-bd syllabus">.*?>.*?>.*?>(.*?)</p>',re.S)
        groups = re.search(pattern, page)
        if groups == None:
            return None
        value = groups.group(0)
        brief = re.findall(pattern, value)
        if brief:
            return brief
        else:
            return None

    def getClassInfo(self, page):
        page = page.replace(r'<br>','')
        infos = ''
        flag = True

        brief  = self.getBrief_4(page)
        if brief:
            for info in brief:
                infos = infos+info[0]
                name = info[1]
                pos = name.find('<p>')
                pos_1 = name.find('<h3>')
                pos_2 = name.find('</ul>')
                if pos < 0 and pos_1 < 0:
                    infos = infos+info[0]
                    reg = re.compile(r'<li>(.*?)</li>')
                    li = re.findall(reg, name)
                    for com in li:
                        infos = infos + '\n' + com
                    return infos

        infos = ''
        brief = self.getBrief_3(page)
        if brief:
            for info in brief:
                for name in info:
                    infos = infos+ name
            pos = infos.find('<h3>')
            pos_1 = infos.find('<p>')
            pos_2 = infos.find('</ul>')
            if pos < 0 and pos_1 < 0:
                if pos_2 <0:
                    return infos
        infos = ''
        brief = self.getBrief_1(page)
        if brief:
            for info in brief:
                for nn in info:
                    infos = infos+ nn
            pos  = infos.find('<h3>')
            pos_1 = infos.find('<p>')
            pos_2 = infos.find('</ul>')
            if pos < 0 and pos_1 < 0:
                return infos

        infos = ''
        brief = self.getBrief(page)
        if brief:
            value = brief[0]
            pos = value.find('<h3>')
            pos_1 = value.find('<p>')
            pos_2 = value.find('</ul>')
            if pos < 0 and pos_1 < 0:
                if pos_2 < 0:
                    return brief[0]
        infos = ''
        brief = self.getBrief_5(page)
        if brief:
            value = brief[0]
            pos = value.find('<h3>')
            pos_1 = value.find('<p>')
            pos_2 = value.find('</ul>')
            if pos < 0 and pos_1 < 0:
                if pos_2 < 0:
                    return brief[0]
        return None

    def getCourceInfo(self):
        cource_url_list = self.getCourceUrl(self.url)
        conn = MysqlHelper.connect()
        cur = conn.cursor()
        cur.execute('drop table if exists jisuanke')
        cur.execute('create table jisuanke(id int(11) primary key auto_increment,title varchar(255),time varchar(255),learn_count varchar(255),short_desc text,outline text)')
        sql = 'insert into jisuanke(title,time,learn_count,short_desc,outline) values(%s,%s,%s,%s,%s)'

        #file = open("JiSuanke.txt","w+")
        for pageurl in cource_url_list:
            value = []
            cource_url = "http:" + pageurl
            page = self.getPageInfo(cource_url)
            courceName = self.getCourceName(page)
            title = self.removeTab(courceName[0])
            value.append(title)
            #file.write('\n'+'课程题目：' + title)
            #print title
            #print courceName[0]
            courceTime = self.getCourceTime(page)
            times = self.removeTab(courceTime[0])
            value.append(times)
            #file.write('\n'+'课程时长：' + times)
            #print times
            peopleNum = self.getPeopleNum(page)
            value.append( peopleNum[0])
            #file.write('\n'+'学习人数：' + peopleNum[0])
            #print peopleNum[0]
            #brief = self.getBrief(page)
            #file.write('\n'+'课程介绍：'+ brief[0])
            brief = self.getClassInfo(page)
            value.append(brief)
            #print brief
            #file.write('\n' + '课程介绍：' + brief)

            courseInfo= self.getInfo(page)
            #file.write('\n'+'课程目录：')
            str = ""
            if courseInfo:
                for item in courseInfo:
                    str= str + item[0] + ':' + item[1] + '\n'
                    #file.write('\n\t' + item[0] + '：' + item[1])
                    #print item[0]
                    #print item[1]
                    pattern = re.compile(r'<li>(.*?)</li>',re.S)
                    li = re.findall(pattern, item[2])
                    for info in li:
                        str = str + info

            value.append(str)
            MysqlHelper.insert_one(cur,sql,value)
        MysqlHelper.finish(conn)
                        #file.write('\n\t\t' + info)
                        #print info
            #file.write('\n')
        #file.close()


if __name__ == "__main__":
    baseUrl = "http://www.jisuanke.com/course"
    jisuanke = JiSuanKe(baseUrl)
    jisuanke.getCourceInfo()
