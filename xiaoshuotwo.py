import os
from time import sleep
import requests
import parsel
from parsel import Selector #请求网页html数据
import pymysql #请求数据库


# 从chapter_url中得到小说的名字对应的xiaoshuoid  chapter_urlshuzu[4]，然后从章节中得到zhangjieid chapter_urlshuzu[5].split('.')[0],章节内容是for循环里所有 利用test 和章节名称就是title好拿
def download_one_chapter(chapter_url,bookname,lebieming): #爬取单一章节内容代码块，函数
    response=requests.get(chapter_url)
    chapter_urlshuzu=chapter_url.split('/') #拆分章节url，通过切片获取需要的信息
    response.encoding=response.apparent_encoding    #字符编码 自动识别
    # response.encoding = 'utf-8' 手动改变字符编码
    # 提取网页内容的方法：正则表达式：提取字符串   xpath css选择器 提取网页数据结构（html） 语法糖 或者 lxml pyquery parsel

    sel=Selector(response.text) # 提取网页小说内容
    title=sel.css('h1::text').get()
    f=open('biquge/'+lebieming+'/'+bookname+'/'+title+'.txt',mode='w',encoding='utf-8')     # f 打开的文件对象 打开文件，创建文件
    f.write(title)
    for line in sel.css('#content::text').getall():
        print(line.strip(),file=f) #逐行读入
    f.close()  # 关闭文件

    # 连接数据库
    conn = pymysql.connect(host='localhost',port=3306,user='root',passwd='123456',db='xiaoshuo',charset='utf8',)
    cursor = conn.cursor()
    f = open('biquge/' + lebieming + '/' + bookname + '/' + title + '.txt', mode='r', encoding='utf-8')
    while True:
        # 逐行读取
        line = f.readlines()
        if line:
            # 处理每行\n
            line = "".join(line)
            line = line.strip('\n')
            line = line.split(",")
            content = line[0]
            cursor.execute(
                "insert into zhangjie(zhangjieid,zhangjiename,zhangjieleirong,xiaoshuoid) values(%s,%s,%s,%s)",
                [chapter_urlshuzu[5].split('.')[0],title,content,chapter_urlshuzu[4]])
        else:
            break
    f.close()
    cursor.close()
    conn.commit()
    conn.close()

# xiaoshuoming就是bookname xiaoshuoid就是book_url里的参数book_urlshuzu[4] xiaoshuofenleiid就是用lebieming对应数组来取leibieshuzu.index(lebieming)+1
def download_one_book(book_url,bookname,lebieming): # 下载一本小说
    response=requests.get(book_url)
    book_urlshuzu=book_url.split('/')
    response.encoding=response.apparent_encoding
    sel=Selector(response.text)
    if os.path.exists('biquge/' + lebieming + '/' + bookname): # 创建小说的文件夹
        print("已存储有" + bookname + "小说")
        return
    if not os.path.exists('biquge/' + lebieming + '/' + bookname):
        os.mkdir('biquge/' +lebieming+'/'+ bookname)
        leibieshuzu=['玄幻','武侠','都市','历史','侦探','网游','科幻']
        xiaoshuoimg='http://www.shuquge.com/files/article/image/'+book_urlshuzu[4][0:len(book_urlshuzu[4])-3]+'/'+book_urlshuzu[4]+'/'+book_urlshuzu[4]+'s.jpg'
        # 连接数据库
        conn = pymysql.connect(host='localhost',port=3306,user='root',passwd='123456',db='xiaoshuo',charset='utf8',)
        cursor = conn.cursor()
        cursor.execute(
            "insert into xiaoshuoinfo(xiaoshuoid,xiaoshuoname,xiaoshuofenleiid,xiaoshuoimg) values(%s,%s,%s,%s)",
            [book_urlshuzu[4],bookname,leibieshuzu.index(lebieming)+1,xiaoshuoimg])
        cursor.close()
        conn.commit()
        conn.close()
        i=0;
        index=sel.css('.listmain a::attr(href)').getall()
        # 限制不下载前十二章
        # print(index)
        # for line in index:
        #     i+=1
        #     # print('http://www.shuquge.com/txt/'+ book_urlshuzu[4]+'/'+line)
        #     if i>12:
        #         download_one_chapter('http://www.shuquge.com/txt/'+ book_urlshuzu[4]+'/'+line,bookname,lebieming)
        download_one_chapter('http://www.shuquge.com/txt/'+ book_urlshuzu[4]+'/'+index[12],bookname,lebieming)
        download_one_chapter('http://www.shuquge.com/txt/'+ book_urlshuzu[4]+'/'+index[13],bookname,lebieming)
        print("读取"+bookname+"小说完成")

# 下载单一类别小说
def download_category(category_url,leibieming):
    response = requests.get(category_url)
    response.encoding = response.apparent_encoding
    sel = Selector(response.text)
    os.mkdir('biquge/' + leibieming)
    if os.path.exists('biquge/' + leibieming):
        index2 = sel.css('span.s2 a::text').getall()
        i=0
        index = sel.css('span.s2 a::attr(href)').getall()
        for line in index:
            download_one_book(line,index2[i],leibieming)
            i+=1

def download_allcategory(website_url): # 下载全部类别的小说
    response = requests.get(website_url)
    response.encoding = response.apparent_encoding
    sel = Selector(response.text)
    index2 = sel.css('.nav a::text').getall()
    i=1
    j=1
    index = sel.css('.nav a::attr(href)').getall()
    for line in index:
        if i>=8:
            break
        if j!=0 and j<8:
            print(line)
            download_category(line, index2[i])
        i+=1
        j+=1

download_allcategory('http://www.shuquge.com/')