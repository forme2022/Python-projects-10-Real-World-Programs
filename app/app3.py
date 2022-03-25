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
                    response=requests.get("https://restapi.amap.com/v3/geocode/geo?address="+address+"&output=JSON&key=xxxx")
                    sText = response.text
                    resData = json.loads(sText)
                    locationList.append(resData["geocodes"][0]["location"])
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


if __name__=='__main__':
    app.run(debug=True)