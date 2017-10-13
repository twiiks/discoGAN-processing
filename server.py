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
from written2all import written2all

app = Flask(__name__)


# result test
# def testDumpResult(handwritesDic):
#     afterTestResultDic = {}
#     print(handwritesDic)
#     with open(handwritesDic[45572], 'rb') as image_file:
#         afterTestResultDic[ord('폰')] = base64.b64encode(image_file.read()).decode('utf-8')
#     with open(handwritesDic[48528], 'rb') as image_file:
#         afterTestResultDic[ord('토')] = base64.b64encode(image_file.read()).decode('utf-8')
#     return afterTestResultDic


def scale(image, max_size, method=Image.ANTIALIAS):
    im_aspect = float(image.size[0]) / float(image.size[1])
    out_aspect = float(max_size[0]) / float(max_size[1])
    if im_aspect >= out_aspect:
        scaled = image.resize((max_size[0], int((float(max_size[0]) / im_aspect) + 0.5)), method)
    else:
        scaled = image.resize((int((float(max_size[1]) * im_aspect) + 0.5), max_size[1]), method)

    offset = (int((max_size[0] - scaled.size[0]) / 2), int((max_size[1] - scaled.size[1]) / 2))
    print(offset)
    back = Image.new("RGB", max_size, "white")
    back.paste(scaled, offset)
    return back


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
        dir = './data/{}/A'.format(hex(fileName).upper().split('X')[1])
        if not os.path.exists(dir):
            os.makedirs(dir)

        im = scale(im, [64, 64])
        im.save(dir + '/{}.jpg'.format(fileName), 'JPEG')
        return dir[:-2]


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
    result = written2all(handwritesDic)
    return result


@app.route('/')
def test_root():
    return 'OK'


if __name__ == '__main__':
    app.run(port=5959, debug=True)
