from distutils.log import debug
from email.mime import text
from fileinput import filename
import gc
from time import strftime
from flask import Flask, render_template, request, send_file
#from geopy.geocoders import Nominatim
#from geopy.geocoders import ArcGIS
#from geopy.geocoders import GoogleV3
import requests
import json
import pandas
import datetime 

# -*- coding: utf-8 -*- 
# 第一行必须有，否则报中文字符非ascii码错误
import urllib
from urllib.request import urlopen, quote
from urllib import parse
import hashlib


app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/success-table', methods=['POST'])
def success_table():
    global filename
    if request.method=="POST":
        #if  'file' in request.files:
            #return render_template("index.html", text="没有选择上传文件")
        file=request.files['file']
        try:
            df=pandas.read_csv(file)
            if  'Address' in df:
                print("Address 存在")
                locationList = []
                for address in df["Address"]:
                    #locationList.append(gaode(address))
                    locationList.append(tx(address))
                    #locationList.append(baidu(address))
                df['location'] = locationList
            else :
                print("Address 不存在")
                return render_template("index.html", text="Address 不存在")
            filename=datetime.datetime.now().strftime("sample_files/%Y-%m-%d-%H-%M-%S-%f"+".csv")
            df.to_csv(filename,index=None)
            return render_template("index.html", text=df.to_html(), btn='download.html')
        except Exception as e:
            print(e)
            return render_template("index.html", text=str(e))

@app.route("/download-file/")
def download():
    return send_file(filename, attachment_filename='yourfile.csv', as_attachment=True)

def gaode(address):
    response=requests.get("https://restapi.amap.com/v3/geocode/geo?address="+address+"&output=JSON&key=xxxx")
    sText = response.text
    resData = json.loads(sText)
    return resData["geocodes"][0]["location"]
    #在一起的经纬度如何分割开在2列中呈现?
    #coords = '121.6788,31.8713'
    #longitude = coords.split(',')[0]
    #latitude  = coords.split(',')[1]
    #print (longitude); print (latitude)

    #引入re模块，“re”是“Regular Expression”的缩写，即正则表达式。由于经纬度是用逗号分离，因而这里用的代码很简单，只能算是正则表达式的小试牛刀。
    # 以启东市经纬度为例 import recoords = '121.6788,31.8713'          
    # 利用经纬度间的逗号将二者分开 m = re.search('(.*),(.*)', coords)   
    # 经度位于第一个括号longitude = m.group(1)                   
    # 纬度位于第二个括号latitude = m.group(2) 
    #print (longitude); print (latitude)
    

def tx(address):
    response=requests.get("https://apis.map.qq.com/ws/geocoder/v1/?address="+address+"&key=xxxx")
    sText = response.text
    resData = json.loads(sText)
    print(resData)
    location = resData["result"]["location"]
    return str(location["lng"]) + "," + str(location["lat"])
    #已分开的经纬度如何在2列中呈现?
    

def baidu(address):
    # 以get请求为例https://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak
    #queryStr = '/geocoding/v3/?address=龙华区致远中路深圳北站西广场&output=json&ak=xxxx'
    queryStr = '/geocoding/v3/?address='+address+'&output=json&ak=xxxx'

    # 对queryStr进行转码，safe内的保留字符不转换
    #encodedStr = urllib.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    encodedStr = quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    print(encodedStr)

    # 在最后直接追加上yoursk
    rawStr = encodedStr + 'fXRrE0WooZ2hlC7Gqck5704S52WPsc6q'
    print(rawStr.encode('utf-8'))
    #print(rawStr.encode('utf-8'))
    #print(quote(rawStr).encode('utf-8'))

    # md5计算出的sn值7de5a22212ffaa9e326444c75a58f9a0
    # 最终合法请求url是https://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak&sn=xxxx
    # 我的例 https://api.map.baidu.com/geocoding/v3/?address=龙华区致远中路深圳北站西广场&output=json&ak=xxxx&sn=xxxx
    #print hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()
    md = hashlib.md5()
    #md.update(quote(rawStr).encode('utf-8'))
    md.update(parse.quote_plus(rawStr).encode('utf-8'))
    sn=md.hexdigest()
    print("https://api.map.baidu.com/" + queryStr + "&sn=" + sn)
    response=requests.get("https://api.map.baidu.com" + queryStr + "&sn=" + sn)
    sText = response.text
    resData = json.loads(sText)
    print(resData)
    location = resData["result"]["location"]
    return str(location["lng"]) + "," + str(location["lat"])

if __name__=='__main__':
    app.run(debug=True)