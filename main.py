#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import requests,re,os,execjs
from lxml import etree
from urllib.parse import quote

def downloads(datas:str,path_host=""):
    data_list=datas.split("$")
    name=data_list[0]
    url_Id=data_list[1]
    media_type=data_list[2]
    if media_type == "qqy" :
        ts_url=""
        url="http://v.jialingmm.net/qy1.php?url=https://www.iqiyi.com/v_{0}.html".format(url_Id)
        js_url=etree.HTML(requests.get(url=url).text).xpath("/html/body/script[3]/@src")[0]
        docjs=execjs.compile(requests.get(url=js_url).text)
        for vid_item in docjs.eval('tvInfoJs["data"]["vidl"]'):
            if vid_item["vd"] == 4 :
                ts_url=vid_item["m3u"]
                break
            else :
                ts_url_tmp=vid_item["m3u"]
            if not ts_url :
                ts_url=ts_url_tmp
        rsp_text=requests.get(url=ts_url).text
        if "#EXTM3U" not in rsp_text:
            print("这不是一个m3u8的视频链接！")
            return False
        if "EXT-X-KEY" in rsp_text:
            print("加密了！")
            return False
        ts_pattern=re.compile(r"http://.*?\.ts.*")
        ts_list=ts_pattern.findall(rsp_text)
        with open("%s%s.ts"%(path_host,name),"wb+") as f:
            print("\n","正在下载%s..."%name)
            for ts in ts_list:
                ts_content=requests.get(url=ts).content
                f.write(ts_content)
            print("\n%s下载完成"%name)
            f.close()
    else:
        with open("%s%s.%s"%(path_host,name,media_type),"wb") as f :
            print("\n","正在下载%s..."%name)
            print(url_Id)
            rsp=requests.get(url=url_Id,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75'},stream=True)
            for chunk in rsp.iter_content(chunk_size=5242880) :
                if chunk :                                          
                    f.write(chunk)
            print("\n%s下载完成"%name)
            f.close()


def get_datas(url:str):
    host="http://www.imomoe.ai"
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75'}
    rsp=requests.get(url=url,headers=headers)
    rsp_HTML=etree.HTML(rsp.text)
    js_url=rsp_HTML.xpath("/html/body/div[2]/div[2]/script[1]/@src")
    if len(js_url) :
        js_url = host + js_url[0]
        print(js_url)
    else :
        return 0
    url_json=re.findall(r"var VideoListJson=(\S+),urlinfo",requests.get(url=js_url,headers=headers).text)
    if len(url_json) :
        data_list=eval(url_json[0])
        url_list=data_list[0][1]  
        return url_list
    else :
        return 0
        
def search(name:str):
    search_url="http://www.imomoe.ai/search.asp"
    headers={
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Content-Length':'23',
        'Content-Type':'application/x-www-form-urlencoded',
        'Host':'www.imomoe.ai',
        'Origin':'http://www.imomoe.ai',
        'Referer':'http://www.imomoe.ai/search.asp',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50'
    }
    rsp=requests.post(url=search_url,headers=headers,data="searchword=%s"%name)
    rsp.encoding="gb2312"
    rsp_HTML=etree.HTML(rsp.text)
    result_list=rsp_HTML.xpath("//div[@class='fire l']/div[@class='pics']/ul/li/h2/a")
    if len(result_list) == 0 :
        print("未检索到信息，请重试")
        return 0 
    else:
        i=1
        for result_item in result_list :
            result_name=result_item.xpath("./text()")[0]
            print("{0}.{1}".format(i,result_name))
            i+=1
        index = int(input("请输入序号："))-1
        return [result_list[index].xpath("./@href")[0][6:-5],result_list[index].xpath("./text()")[0]]






if __name__ == "__main__":  

    result = search(quote(input("请输入番剧名称:"),encoding="gb2312"))
    if result :
        print(result[0])
        url="http://www.imomoe.ai/player/{0}-0-0.html".format(result[0])
        datas=get_datas(url)
        if datas :
            if len(datas) > 26 :
                for item_former_index in range(12) :
                    print("%10s %10s"%(datas[item_former_index*2].split("$")[0],datas[item_former_index*2+1].split("$")[0]))
                print("%10s %10s"%("...","..."))
                print("%10s %10s"%("...","..."))
                for item_former_index in range(-12,0) :
                    print("%10s %10s"%(datas[item_former_index*2].split("$")[0],datas[item_former_index*2+1].split("$")[0]))

            else :
                for item_former_index in range(int(len(datas)/2)) :
                    print("%10s %10s"%(datas[item_former_index*2].split("$")[0],datas[item_former_index*2+1].split("$")[0]))
                if len(datas)%2 :
                    print("%10s"%datas[-1].split("$")[0])
            mission=input("请输入你要下载的集数：")
            mission_unit=mission.split(",")
            if len(mission_unit)==1 and  not("--" in mission_unit[0]) :
                downloads(datas[int(mission_unit[0])-1])
            else:
                try:
                    os.mkdir(result[1])
                except Exception as e:
                    pass
                for mission_unit_item in mission_unit :
                    missions=mission_unit_item.split("--")
                    if len(missions) > 1 :  
                        for index in range(int(missions[0]),int(missions[1])+1):
                            downloads(datas[index-1],"./%s/"%result[1])

                    else:
                        downloads(datas[int(mission_unit_item)-1],"./%s/"%result[1])




    