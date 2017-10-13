from flask import Flask, request
import json
import threading
import time

app = Flask(__name__)

def thread_test():
    time.sleep(2)
    print('hi')

@app.route('/fontto/processing', methods=['POST'])
def processing_fontto():
    threading.Thread(target=thread_test).start()
    return json.dumps(request.json)


@app.route('/')
def test_root():
    return 'OK'


if __name__ == '__main__':
    app.run(port=5959,debug=True)
