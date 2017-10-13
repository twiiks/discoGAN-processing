from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/fontto/processing', methods=['POST'])
def processing_fontto():
    print(request.json)
    return json.dumps(request.json)


@app.route('/')
def test_root():
    return 'OK'

if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5959)
    IOLoop.instance().start()
