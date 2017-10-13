# -*- coding: utf-8 -*-

from flask import Flask, request
import json
import threading
import time
import requests
import base64
import os
from PIL import Image, ImageChops
from io import BytesIO

app = Flask(__name__)


# result test
def testDumpResult(handwritesDic):
    afterTestResultDic = {}
    with open(handwritesDic[45572], 'rb') as image_file:
        afterTestResultDic[ord('폰')] = base64.b64encode(image_file.read()).decode('utf-8')
    with open(handwritesDic[46028], 'rb') as image_file:
        afterTestResultDic[ord('토')] = base64.b64encode(image_file.read()).decode('utf-8')
    return afterTestResultDic


# trim from base64 image
def trimAndSave(b64Image, email, fileName):
    bytesIO = BytesIO(base64.b64decode(b64Image))
    bytesIO.seek(0)
    im = Image.open(bytesIO)
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        im = im.crop(bbox)
        # im.show()
        dir = './data/{}'.format(email)
        if not os.path.exists(dir):
            os.makedirs(dir)
        im.save(dir + '/{}.jpg'.format(fileName), 'JPEG')
        return dir + '/{}.jpg'.format(fileName)


# 1. url -> buffer
# 2. buffer -> crop -> save
def makeHandwritesDic(urlList, email):
    handwritesDic = {}
    for url in urlList:
        uniChar = ord(url.split('_')[-1])

        response = requests.get(url)
        # base64 encode
        b64ImageBeforeCrop = base64.b64encode(response.content)
        # base64 crop
        filePath = trimAndSave(b64ImageBeforeCrop, email, uniChar)
        # save cropped image

        handwritesDic[uniChar] = filePath

    return handwritesDic


@app.route('/fontto/processing', methods=['POST'])
def processing_fontto():
    return json.dumps(backgroundProcessing(request))


def backgroundProcessing(request):
    body = request.json
    email = body['email']
    handwritesDic = makeHandwritesDic(body['handwrites'], email)

    # ml code here
    result = testDumpResult(handwritesDic)
    return result


@app.route('/')
def test_root():
    return 'OK'


if __name__ == '__main__':
    app.run(port=5959, debug=True)
