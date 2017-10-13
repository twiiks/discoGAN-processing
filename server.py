#-*- coding: utf-8 -*-

from flask import Flask, request
import json
import threading
import time
import requests
import base64

app = Flask(__name__)

# result test
def testDumpResult(testResultB64):
    afterTestResultDic = {}
    afterTestResultDic[ord('폰')] = testResultB64.decode('utf-8')
    afterTestResultDic[ord('토')] = testResultB64.decode('utf-8')
    return afterTestResultDic

# jpg save test
# def saveB64Image(uniChar, b64Image):
#     fh = open("{}.jpg".format(uniChar), "wb")
#     fh.write(base64.b64decode(b64Image))
#     fh.close()

def makeHandwritesDic(urlList):
    handwritesDic = {}
    for url in urlList:
        # print(url)
        uniChar = ord(url.split('_')[-1])

        response = requests.get(url)
        b64Image = base64.b64encode(response.content)

        # testB64Image(uniChar, b64Image)

        handwritesDic[uniChar] = b64Image
    return handwritesDic


@app.route('/fontto/processing', methods=['POST'])
def processing_fontto():
    return json.dumps(backgroundProcessing(request))

def backgroundProcessing(request):
    body = request.json
    email = body['email']
    handwritesDic = makeHandwritesDic(body['handwrites'])

    # ml code here
    result = testDumpResult(handwritesDic[ord('누')])
    return result


@app.route('/')
def test_root():
    return 'OK'


if __name__ == '__main__':
    app.run(port=5959,debug=True)
