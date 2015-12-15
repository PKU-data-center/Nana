Enter file contents here#get the courses data of Chinese MOOC
#I found that the following url can get all the class info after I analyze the website
#http://www.chinesemooc.org/api/search_by_classid.php?classid=all&page=2
#the parameter value of classid and page can be modified
#Nana Li  2015.12.7
#version 1.0

#-*- coding=utf-8 -*-

import urllib
import urllib2
import time
import re
import MySqlHelper

#for test
import codecs

#global value
false = 0

#define a class to contain the values
#which will insert to db
class Item:
    def __init__(self):
        self.course_id = 0
        self.course_title = ""
        self.course_term = ""
        self.course_outline = ""
        self.course_view_num = 0
        self.course_comment_num = 0
        self.course_price = 0
        self.signup = 0
        self.course_des = ""
        self.teacher_info = ""
        self.assistant = ""
        self.school = ""


def getHtml(url,header):
    req_timeout = 15;
    try:
        req = urllib2.Request(url, None, headers=header)
        page = urllib2.urlopen(url, None, req_timeout)
        if page == None:
            return None
        html = page.read()
        return html
    except urllib2.URLError,e:
        if hasattr(e,"reason"):
            print u"Connect ChineseMooc failed",e.reason
        return None

def uni2utf(string):
    tmp_str = string.decode('unicode-escape')
    tmp_str = tmp_str.encode('utf-8')
    return tmp_str

def getAllCourseInfo(course_list_dic,header,cur,sql):
    if course_list_dic == None:
        return
    if not course_list_dic.has_key('msg'):
        return
    if not course_list_dic['msg'].has_key('list'):
        return
    course_list = course_list_dic['msg']['list']
    course_num = len(course_list)
    file = open("course.txt","w+")
    item_list = []
    for course_index in range(0,course_num):
        item = Item()
        item.course_id = int(course_list[course_index]['kvideoid'])
        print(item.course_id)
        item.course_view_num = int(course_list[course_index]['viewnum'])
        print(item.course_view_num)
        item.course_title = course_list[course_index]['subject']
        item.course_title = uni2utf(item.course_title)
        print(item.course_title)
        item.course_price = int(course_list[course_index]['price'])
        print(item.course_price)
        item.course_signup = int(course_list[course_index]['signup'])
        print(item.course_signup)
        item.comment_num = int(course_list[course_index]['comment_num'])
        print(item.comment_num)
        item.course_des = uni2utf(course_list[course_index]['kvideo_desc'])
        print(item.course_des)
        item.school = course_list[course_index]['teacher_info']['school_name']
        item.school = uni2utf(item.school)
        print(item.school)

        tmp_url = "http://www.chinesemooc.org/mooc/"+str(item.course_id)
        parseCoursePage(tmp_url,header,item)
        item_list.append(item)

        #sleep
        #time.sleep(3)
    for record_item in item_list:
        value = []
        if record_item.course_id == 4407:
            str1 = "test"
        value.append(record_item.course_id)
        value.append(record_item.course_title)
        value.append(record_item.course_term)
        value.append(record_item.course_outline)
        value.append(record_item.course_view_num)
        value.append(record_item.course_comment_num)
        value.append(record_item.course_price)
        value.append(record_item.signup)
        value.append(record_item.course_des)
        value.append(record_item.teacher_info)
        value.append(record_item.assistant)
        value.append(record_item.school)
        test = sql% (value[0],value[1],value[2],value[3],value[4],value[5],value[6],value[7],value[8],value[9],value[10],value[11],)
        MySqlHelper.insert_one(cur,test,None)
    #file.close()

def delete_tags(html_context):
    #replace <p> to \n and two space
    tag_p = re.compile(r'<p.*?>',re.S)
    tmp_val = tag_p.sub('\n',html_context)
    #replace &nbsp;
    tag_sp = re.compile(r'&nbsp;')
    tmp_val = tag_sp.sub(' ',tmp_val)
    #replace &gt; to >
    tag_gt = re.compile(r'&gt;')
    tmp_val = tag_gt.sub('>',tmp_val)
    #replace &lt; to <
    tag_lt = re.compile(r'&lt;')
    tmp_val = tag_lt.sub('<',tmp_val)
    #delete others
    tag_others = re.compile(r'<.*?>')
    tmp_val = tag_others.sub('',tmp_val)
    #delete \n
    tag_enter = re.compile(r'[(\r\n)(\n)]+[ ]*\n')
    tmp_val = tag_enter.sub('\n',tmp_val)

    return tmp_val


def parseCoursePage(url,header,item):
    html_page = getHtml(url,header)
    html_page = str(html_page)
    #course term
    course_term = re.compile(r'<div class="wrapper">\r\n<div class="select-div">.*?<option>(.*?)</option>',re.S)
    course_term_ele = re.search(course_term, html_page)
    if course_term_ele == None:
        print("WARNING:can't get the value of course term")
    else:
        print(course_term_ele.group(1))
        item.course_term = course_term_ele.group(1)
    #course_des and so on
    pattern = re.compile(r'<div class="wrapper">\r\n<div class="section">(.+?)<div class="wrapper">',re.S)
    wrapper_ele = re.search(pattern, html_page)
    if wrapper_ele == None:
        print("WARNING:can't get course information and teacher information")
    else:
        tmp_val = wrapper_ele.group(1)
        #print(tmp_val)
        pattern = re.compile(r'(.+?)<div class="section">(.*?)<div [(id)(class)]+="bottom" [(id)(class)]+="bottom">',re.S)
        wrapper_ele = re.search(pattern,tmp_val)
        if not wrapper_ele == None:
            item.course_outline = delete_tags(wrapper_ele.group(1))
            print(item.course_outline)
            #print(wrapper_ele.group(2))
            pattern = re.compile(r'(.*?)<div class="section">(.*?)</div>',re.S)
            tmp_ele = re.search(pattern,wrapper_ele.group(2))
            if not tmp_ele == None:
                item.teacher_info = delete_tags(tmp_ele.group(1))
                item.assistant = delete_tags(tmp_ele.group(2))
            else:
                item.teacher_info = delete_tags(wrapper_ele.group(2))
            print(item.teacher_info)
            print(item.assistant)
        #for i in range(0,len(wrapper_ele)):
        #    tmp_val = delete_tags(wrapper_ele[i])
        #    print(tmp_val)



        

def getAllCourse():
    #get first course list page and the value of total page
    url = "http://www.chinesemooc.org/api/search_by_classid.php?classid=all";
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0"
    header = {'User-Agent':user_agent}
    html_page = getHtml(url, header)
    if html_page == None:
        print("ERROR:Get data from Chinese Mooc failed...")
        return

    course_list = eval(html_page)
    total_page_num = course_list['msg']['page_total']
    if course_list.has_key('msg') and course_list['msg'].has_key('page_total'):
        total_page_num = course_list['msg']['page_total']

    conn = MySqlHelper.connect()
    cur = conn.cursor()
    cur.execute('drop table if exists chinesemooc')
    cur.execute('create table chinesemooc(course_id int(11) primary key,course_title varchar(255),\
course_term varchar(255),course_outline text,course_view_num int(11),course_comment_num int(11),\
course_price int(11),signup int(11),course_des text,teacher_info text,assistant text,school varchar(255))')
    sql = 'insert into chinesemooc(course_id,course_title,course_term,course_outline,course_view_num,course_comment_num,\
course_price,signup,course_des,teacher_info,assistant,school) values(%d,"%s","%s","%s",%d,%d,%d,%d,"%s","%s","%s","%s")'
    getAllCourseInfo(course_list,header,cur,sql)
    for page_index in range(2,total_page_num+1):
        page_url =url + "&page=" + str(page_index)
        tmp_page = getHtml(page_url,header)
        if tmp_page == None:
            continue

        tmp_course_list = eval(tmp_page)
        getAllCourseInfo(tmp_course_list,header,cur,sql)
        time.sleep(10)
    MySqlHelper.finish(conn)



if __name__ == '__main__':
    getAllCourse()





